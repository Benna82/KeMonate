import io,json,tempfile,os
from unittest.mock import patch
from django.test import TestCase,Client,override_settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from .models import Story

class ArchiveWorkflowTests(TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.override=override_settings(MEDIA_ROOT=self.temp.name);self.override.enable()
        self.addCleanup(self.temp.cleanup);self.addCleanup(self.override.disable)
        self.owner=get_user_model().objects.create_user('storykeeper',password='River-Stories-762!')
        self.other=get_user_model().objects.create_user('visitor',password='River-Stories-762!')
        self.client.force_login(self.owner)
        self.story=Story.objects.create(owner=self.owner,title='A family story',creator='The storyteller',source_text='My grandmother taught me to weave.')
    def update(self,**data):return self.client.patch(f'/api/stories/{self.story.pk}/',json.dumps(data),content_type='application/json')
    def test_review_consent_publish_withdraw(self):
        self.assertEqual(self.update(status='published').status_code,400)
        self.assertEqual(self.update(consent=True,reviewed=True,status='published').status_code,200)
        public=Client();self.assertEqual(len(public.get('/api/stories/').json()['stories']),1)
        self.assertEqual(self.update(consent=False).json()['status'],'draft')
        self.assertEqual(public.get(f'/api/stories/{self.story.pk}/').status_code,404)
        self.assertEqual(public.get('/api/stories/').json()['stories'],[])
    def test_edit_clears_review_and_restricts_publication(self):
        self.update(consent=True,reviewed=True,status='published')
        changed=self.update(source_text='Corrected source.',reviewed=True).json()
        self.assertFalse(changed['reviewed']);self.assertEqual(changed['status'],'draft')
        self.update(reviewed=True,restrictions='Community only')
        self.assertEqual(self.update(status='published').status_code,400)
    def test_other_account_cannot_read_private_media_or_change_story(self):
        img=io.BytesIO();Image.new('RGB',(5,5),'red').save(img,'PNG')
        response=self.client.post(f'/api/stories/{self.story.pk}/upload/',{'file':SimpleUploadedFile('art.png',img.getvalue(),'image/png')})
        self.assertEqual(response.status_code,200)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(f'/api/stories/{self.story.pk}/').status_code,404)
        self.assertEqual(self.client.get(f'/api/stories/{self.story.pk}/media/').status_code,404)
        self.assertEqual(self.update(title='stolen').status_code,404)
        self.assertEqual(self.client.get(f'/api/stories/{self.story.pk}/export/').status_code,404)
    def test_malformed_upload_rejected_and_delete_removes_media(self):
        url=f'/api/stories/{self.story.pk}/upload/'
        self.assertEqual(self.client.post(url,{'file':SimpleUploadedFile('bad.png',b'<script>alert(1)</script>','image/png')}).status_code,400)
        img=io.BytesIO();Image.new('RGB',(5,5),'red').save(img,'PNG')
        self.client.post(url,{'file':SimpleUploadedFile('art.png',img.getvalue(),'image/png')})
        self.story.refresh_from_db();path=self.story.media.path;self.assertTrue(os.path.exists(path))
        self.client.delete(f'/api/stories/{self.story.pk}/');self.assertFalse(os.path.exists(path))
    def test_ai_requires_separate_permission_and_never_autopublishes(self):
        url=f'/api/stories/{self.story.pk}/ai/'
        with patch('archive.views.process',return_value={'translation':'Translated text','language':'English','reviewed':False,'status':'draft'}) as mock:
            self.assertEqual(self.client.post(url,{'action':'translate'}).status_code,400);mock.assert_not_called()
            self.update(consent=True,ai_consent=True,reviewed=True,status='published')
            response=self.client.post(url,{'action':'translate'})
            self.assertEqual(response.status_code,200);self.assertEqual(response.json()['status'],'draft');self.assertFalse(response.json()['reviewed'])
    def test_missing_key_is_honest(self):
        self.update(ai_consent=True)
        with patch.dict(os.environ,{'OPENAI_API_KEY':''}):
            response=self.client.post(f'/api/stories/{self.story.pk}/ai/',{'action':'generate'})
        self.assertEqual(response.status_code,400);self.assertIn('not configured',response.json()['error'])
    def test_csrf_and_passwords(self):
        c=Client(enforce_csrf_checks=True)
        self.assertEqual(c.post('/api/auth/register/',{'username':'new','password':'somepass'}).status_code,403)
        c.get('/api/session/');token=c.cookies['csrftoken'].value
        self.assertEqual(c.post('/api/auth/register/',{'username':'new','password':'123'},HTTP_X_CSRFTOKEN=token).status_code,400)
        response=c.post('/api/auth/register/',{'username':'new','password':'OralArchive!685'},HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code,200)
        u=get_user_model().objects.get(username='new');self.assertNotEqual(u.password,'OralArchive!685');self.assertTrue(u.check_password('OralArchive!685'))
    def test_export_has_source_and_audit_trail(self):
        self.update(language='English')
        response=self.client.get(f'/api/stories/{self.story.pk}/export/')
        self.assertEqual(response.status_code,200);data=json.loads(response.content)
        self.assertEqual(data['source_text'],self.story.source_text);self.assertTrue(data['events'])
