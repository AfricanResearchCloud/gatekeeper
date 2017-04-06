from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from onboarding.openstack import Openstack
import os

SHIB_USER_ATTRIBUTE = getattr(settings, 'SHIB_USER_ATTRIBUTE')


def index(request):
    username = request.META.get(SHIB_USER_ATTRIBUTE)
    openstack_client = Openstack(username=username)
    # Check if user is registered
    if openstack_client.is_registered_user():
        if openstack_client.is_terms_signed():
            if openstack_client.is_trial_created():
                #Redirect to return URL
                return HttpResponseRedirect(request.GET['return'])
            else:
                #For now, we're not creating trail projects.. so we'll just return to keystone anyway...
                return HttpResponseRedirect(request.GET['return'])
        else:
            return HttpResponse("Please sign terms")
    else:
        if openstack_client.is_user_create_allowed():
            return HttpRespone("User create allow!!!")
        else:
            return HttpResponse("Sorry, no access for you.")

    return HttpResponse("Hello, world. You're at the polls index.")
