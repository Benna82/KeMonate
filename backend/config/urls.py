from django.urls import path,re_path,include
from django.views.generic import TemplateView
from django.contrib.staticfiles.views import serve
from django.views.static import serve as public_serve
from django.conf import settings
urlpatterns=[path('api/',include('archive.urls')),path('africa.json',public_serve,{'path':'africa.json','document_root':settings.BASE_DIR.parent/'frontend'/'dist'}),re_path(r'^images/(?P<path>.*)$',public_serve,{'document_root':settings.BASE_DIR.parent/'frontend'/'dist'/'images'}),re_path(r'^assets/(?P<path>.*)$',serve),re_path(r'^(?!api/).*$',TemplateView.as_view(template_name='index.html'))]
