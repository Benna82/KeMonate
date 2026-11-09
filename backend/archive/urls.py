from django.urls import path
from . import views
urlpatterns=[path('session/',views.session),path('auth/<str:action>/',views.account),path('stories/',views.stories),path('stories/<int:pk>/',views.detail),path('stories/<int:pk>/upload/',views.upload),path('stories/<int:pk>/media/',views.media),path('stories/<int:pk>/ai/',views.ai),path('stories/<int:pk>/export/',views.export)]
