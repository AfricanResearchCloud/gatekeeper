from django.conf.urls import url
from . import views

urlpatterns = [
  url(r'getProjectList$', views.getProjectList, name='getProjectList'),
  url(r'projectAccess/request/(.*)$', views.requestProjectAccess, name='requestProjectAccess'),
  url(r'projectAccess/grant/(.*)/(.*)$', views.grantProjectAccess, name='grantProjectAccess')
]
