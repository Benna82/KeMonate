from django.db import models
from django.conf import settings
import uuid
from pathlib import Path

def upload_path(instance,filename):
    return f'{instance.owner_id}/{uuid.uuid4().hex}{Path(filename).suffix.lower()}'

class Story(models.Model):
    owner=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    title=models.CharField(max_length=180)
    creator=models.CharField(max_length=120)
    country=models.CharField(max_length=80,default='South Africa')
    region=models.CharField(max_length=120,blank=True)
    language=models.CharField(max_length=80,default='Unknown')
    category=models.CharField(max_length=50,default='Storytelling')
    source_text=models.TextField(blank=True)
    translation=models.TextField(blank=True)
    drafts=models.JSONField(default=dict,blank=True)
    media=models.FileField(upload_to=upload_path,blank=True)
    media_type=models.CharField(max_length=100,blank=True)
    consent=models.BooleanField(default=False)
    ai_consent=models.BooleanField(default=False)
    restrictions=models.TextField(blank=True)
    reviewed=models.BooleanField(default=False)
    status=models.CharField(max_length=20,default='draft')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

class AuditEvent(models.Model):
    story=models.ForeignKey(Story,on_delete=models.CASCADE,related_name='events')
    action=models.CharField(max_length=80)
    created_at=models.DateTimeField(auto_now_add=True)
