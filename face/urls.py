from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^person/(?P<pk>\d+).jpg$', views.person_photo, name='person_photo'),
]

