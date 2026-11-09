import json,os,mimetypes
from pathlib import Path
from functools import wraps
from django.http import JsonResponse,FileResponse,Http404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate,login,logout,get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from openai import APIConnectionError,AuthenticationError,RateLimitError
from .models import Story,AuditEvent
from .ai import process,AIError

CATEGORIES=['Painting','Music','Poetry','Oral History','Storytelling','Literature','Sculpture','Dance','Film','Community Heritage']
ALLOWED={'.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.webp':'image/webp','.mp3':'audio/mpeg','.wav':'audio/wav','.m4a':'audio/mp4','.webm':'audio/webm','.ogg':'audio/ogg','.mp4':'video/mp4','.mov':'video/quicktime'}

def body(request):
    return json.loads(request.body or '{}') if request.content_type=='application/json' else request.POST.dict()

def api(fn):
    @wraps(fn)
    def wrapper(request,*args,**kwargs):
        try: return fn(request,*args,**kwargs)
        except (ValueError,TypeError,json.JSONDecodeError): return JsonResponse({'error':'Invalid request data.'},status=400)
    return wrapper

def auth(fn):
    @wraps(fn)
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated: return JsonResponse({'error':'Please sign in first.'},status=401)
        return fn(request,*args,**kwargs)
    return wrapper

def serialize(s):
    return {k:getattr(s,k) for k in ['id','title','creator','country','region','language','category','source_text','translation','drafts','consent','ai_consent','restrictions','reviewed','status']}|{'media_url':f'/api/stories/{s.id}/media/' if s.media else '', 'media_type':s.media_type,'updated_at':s.updated_at.isoformat(),'owner':s.owner.username}

@ensure_csrf_cookie
@require_http_methods(['GET'])
def session(request):
    return JsonResponse({'user':request.user.username if request.user.is_authenticated else None,'ai_enabled':bool(os.environ.get('OPENAI_API_KEY')),'categories':CATEGORIES})

@require_http_methods(['POST'])
@api
def account(request,action):
    data=body(request)
    if action not in ['register','login','logout']: return JsonResponse({'error':'Unknown account action.'},status=400)
    if action=='logout': logout(request); return JsonResponse({'user':None})
    username=data.get('username','').strip(); password=data.get('password','')
    if action=='register':
        if not username or len(username)>150 or not all(c.isalnum() or c in '@.+-_' for c in username): return JsonResponse({'error':'Use a username of up to 150 letters, numbers, or @ . + - _.'},status=400)
        user=get_user_model()(username=username)
        try: validate_password(password,user)
        except ValidationError as e: return JsonResponse({'error':' '.join(e.messages)},status=400)
        try: user=get_user_model().objects.create_user(username=username,password=password)
        except IntegrityError: return JsonResponse({'error':'That username is already taken.'},status=400)
    else:
        user=authenticate(request,username=username,password=password)
        if not user: return JsonResponse({'error':'Username or password is incorrect.'},status=400)
    login(request,user)
    return JsonResponse({'user':user.username})

@require_http_methods(['GET','POST'])
@api
def stories(request):
    if request.method=='GET':
        query=Story.objects.filter(status='published',consent=True,reviewed=True)
        if request.GET.get('mine')=='1':
            if not request.user.is_authenticated: return JsonResponse({'error':'Please sign in first.'},status=401)
            query=Story.objects.filter(owner=request.user)
        return JsonResponse({'stories':[serialize(s) for s in query.order_by('-updated_at')]})
    if not request.user.is_authenticated: return JsonResponse({'error':'Please sign in first.'},status=401)
    data=body(request)
    if not data.get('title','').strip() or not data.get('creator','').strip(): return JsonResponse({'error':'A story title and creator name are required.'},status=400)
    if len(data['title'])>180 or len(data['creator'])>120: return JsonResponse({'error':'Title or creator name is too long.'},status=400)
    s=Story.objects.create(owner=request.user,title=data['title'].strip(),creator=data['creator'].strip())
    AuditEvent.objects.create(story=s,action='created')
    return JsonResponse(serialize(s),status=201)

@require_http_methods(['GET','PATCH','DELETE'])
@api
def detail(request,pk):
    s=get_object_or_404(Story,pk=pk)
    own=request.user.is_authenticated and s.owner_id==request.user.id
    if not own and not (s.status=='published' and s.consent and s.reviewed): raise Http404
    if request.method=='GET': return JsonResponse(serialize(s))
    if not own: return JsonResponse({'error':'Only the story owner can change this story.'},status=403)
    if request.method=='DELETE':
        if s.media: s.media.delete(save=False)
        s.delete(); return JsonResponse({'deleted':True})
    data=body(request)
    allowed={'title':180,'creator':120,'country':80,'region':120,'language':80,'category':50,'source_text':60000,'translation':60000,'restrictions':4000}
    for k,limit in allowed.items():
        if k in data:
            if not isinstance(data[k],str) or len(data[k])>limit: return JsonResponse({'error':f'Invalid {k}.'},status=400)
            if k in ('title','creator') and not data[k].strip(): return JsonResponse({'error':f'{k} is required.'},status=400)
            if k=='category' and data[k] not in CATEGORIES: return JsonResponse({'error':'Unknown category.'},status=400)
            setattr(s,k,data[k])
    for k in ['consent','ai_consent','reviewed']:
        if k in data:
            if not isinstance(data[k],bool): return JsonResponse({'error':f'{k} must be true or false.'},status=400)
            setattr(s,k,data[k])
    if 'drafts' in data:
        if not isinstance(data['drafts'],dict) or any(not isinstance(v,str) or len(v)>60000 for v in data['drafts'].values()): return JsonResponse({'error':'Drafts must contain text.'},status=400)
        s.drafts=data['drafts']
    changed=any(k in data and data[k]!=getattr(Story.objects.get(pk=pk),k) for k in ['source_text','translation','drafts'])
    if changed: s.reviewed=False; s.status='draft'
    if 'status' in data:
        if data['status'] not in ['draft','published']: return JsonResponse({'error':'Unknown status.'},status=400)
        if data['status']=='published' and (not s.consent or not s.reviewed or s.restrictions.strip() or not (s.source_text.strip() or s.translation.strip())): return JsonResponse({'error':'Before publishing: confirm permission, review the saved content, add source text, and resolve cultural restrictions. Restricted stories remain private.'},status=400)
        s.status=data['status']
    if not s.consent or not s.reviewed or s.restrictions.strip(): s.status='draft'
    s.save(); AuditEvent.objects.create(story=s,action='updated / '+s.status)
    return JsonResponse(serialize(s))

@require_http_methods(['POST'])
@auth
@api
def upload(request,pk):
    s=get_object_or_404(Story,pk=pk,owner=request.user)
    f=request.FILES.get('file')
    if not f: return JsonResponse({'error':'Choose a file.'},status=400)
    ext=Path(f.name).suffix.lower()
    if ext not in ALLOWED or f.size>24*1024*1024 or f.size==0: return JsonResponse({'error':'Use JPG, PNG, WebP, MP3, WAV, M4A, OGG, WebM, MP4 or MOV up to 24 MB.'},status=400)
    head=f.read(32); f.seek(0)
    valid=True
    if ALLOWED[ext].startswith('image/'):
        from PIL import Image
        try: Image.open(f).verify(); f.seek(0)
        except Exception: valid=False
    elif ext=='.wav': valid=head[:4]==b'RIFF' and head[8:12]==b'WAVE'
    elif ext in ['.mp4','.mov','.m4a']: valid=head[4:8]==b'ftyp'
    elif ext=='.webm': valid=head[:4]==bytes.fromhex('1a45dfa3')
    elif ext=='.ogg': valid=head[:4]==b'OggS'
    elif ext=='.mp3': valid=head[:3]==b'ID3' or (len(head)>1 and head[0]==255 and head[1]&224==224)
    if not valid: return JsonResponse({'error':'The file contents do not match a supported media format.'},status=400)
    if s.media: s.media.delete(save=False)
    s.media=f; s.media_type=('video/webm' if ext=='.webm' and f.content_type=='video/webm' else ALLOWED[ext]); s.reviewed=False; s.status='draft'; s.save()
    AuditEvent.objects.create(story=s,action='media replaced')
    return JsonResponse(serialize(s))

@require_http_methods(['GET'])
def media(request,pk):
    s=get_object_or_404(Story,pk=pk)
    if not ((request.user.is_authenticated and s.owner_id==request.user.id) or (s.status=='published' and s.consent and s.reviewed)): raise Http404
    if not s.media: raise Http404
    response=FileResponse(s.media.open('rb'),content_type=s.media_type)
    response['Cache-Control']='private, no-store'; response['X-Content-Type-Options']='nosniff'
    return response

@require_http_methods(['POST'])
@auth
@api
def ai(request,pk):
    s=get_object_or_404(Story,pk=pk,owner=request.user)
    if not s.ai_consent: return JsonResponse({'error':'Confirm permission to send this material to OpenAI first.'},status=400)
    action=body(request).get('action')
    if action not in ['transcribe','translate','generate']: return JsonResponse({'error':'Unknown AI action.'},status=400)
    try: changes=process(s,action)
    except AIError as e: return JsonResponse({'error':str(e)},status=400)
    except AuthenticationError: return JsonResponse({'error':'OpenAI rejected the API key. Check that the server is using a valid API key, then restart it.'},status=502)
    except RateLimitError as e:
        if getattr(e,'code',None)=='insufficient_quota': return JsonResponse({'error':'The OpenAI API account has no credits remaining. Add API credits or enable billing, then try again. Your story is unchanged.'},status=429)
        return JsonResponse({'error':'The OpenAI API rate limit was reached. Wait a moment and try again. Your story is unchanged.'},status=429)
    except APIConnectionError: return JsonResponse({'error':'Could not connect to OpenAI. Check your internet connection and try again. Your story is unchanged.'},status=502)
    except Exception: return JsonResponse({'error':'The AI service could not complete the request. Check the server API key, model access, quota and internet connection. Your existing story is unchanged.'},status=502)
    for k,v in changes.items(): setattr(s,k,v)
    s.save(); AuditEvent.objects.create(story=s,action='AI '+action+'; human review required')
    return JsonResponse(serialize(s))

@require_http_methods(['GET'])
@auth
def export(request,pk):
    s=get_object_or_404(Story,pk=pk,owner=request.user)
    from django.http import HttpResponse
    payload=serialize(s); payload['events']=list(s.events.values('action','created_at')); payload['export_note']='Original source, translation and drafts are separate. Creator retains authorship. Media must be backed up separately.'
    response=HttpResponse(json.dumps(payload,ensure_ascii=False,indent=2,default=str),content_type='application/json')
    response['Content-Disposition']=f'attachment; filename="kemonate-story-{s.id}.json"'
    return response
