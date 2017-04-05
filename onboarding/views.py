from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from onboarding.openstack import Openstack
import os

SHIB_USER_ATTRIBUTE = getattr(settings, 'SHIB_USER_ATTRIBUTE')

def index(request):
    openstack_client = Openstack()
    # Check for Shibboleth Session
    username = request.META.get(SHIB_USER_ATTRIBUTE)
    # Query Keystone for user

    return HttpResponse("Hello, world. You're at the polls index.")
