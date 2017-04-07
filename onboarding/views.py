from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.template import loader
from onboarding.openstack import Openstack
import markdown
import os

SHIB_USER_ATTRIBUTE = getattr(settings, 'SHIB_USER_ATTRIBUTE')


def index(request):
    #username = request.META.get(SHIB_USER_ATTRIBUTE)
    username = 'stefan.coetzee@uct.ac.za'
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
            terms_markdown = open('onboarding/markdown/terms.md', 'r').read()
            template = loader.get_template('onboarding/display_terms.html')
            return HttpResponse(template.render({'terms_markdown' : markdown.markdown(terms_markdown), 'title': 'Sign Terms'}))
    else:
        if openstack_client.is_user_create_allowed():
            return HttpRespone("User create allow!!!")
        else:
            return HttpResponse("Sorry, no access for you.")

    return HttpResponse("Hello, world. You're at the polls index.")
