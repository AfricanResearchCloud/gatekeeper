from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^signTerms$', views.signTerms, name='signTerms'),
    url(r'^getUser$', views.getUser, name='getUser'),
    url(r'^getTerms$', views.getTerms, name='getTerms'),
    url(r'^createUser$', views.createUser, name='createUser'),
    url(r'^getWelcome$', views.getWelcome, name='getWelcome'),
    url(r'^getNotAllowedCreate$', views.getNotAllowedCreate, name='getNotAllowedCreate')
]
