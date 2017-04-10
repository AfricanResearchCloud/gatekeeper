from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^signTerms$', views.signTerms, name='signTerms'),
    url(r'^getUser$', views.getUser, name='getUser'),
    url(r'^getTerms$', views.getTerms)
]
