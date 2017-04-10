from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.template import loader
from onboarding.openstack import Openstack
from django.views.decorators.csrf import csrf_exempt
from onboarding.user import User
import markdown
import os
import json

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
            if hasattr(request.GET, 'isTermsAgree') and request.GET['isTermsAgree'] == 'true':
                return HttpResponse('Terms Signed now !!')
            terms_markdown = open('onboarding/markdown/terms.md', 'r').read()
            template = loader.get_template('onboarding/display_terms.html')
            return HttpResponse(template.render({'terms_markdown' : markdown.markdown(terms_markdown), 'title': 'Sign Terms'}))
    else:
        if openstack_client.is_user_create_allowed():
            return HttpRespone("User create allow!!!")
        else:
            return HttpResponse("Sorry, no access for you.")
    return HttpResponse("Hello, world. You're at the polls index.")

@csrf_exempt
def signTerms(request):
    username = request.META.get(SHIB_USER_ATTRIBUTE)
    return HttpResponse('Terms Signed now !!')

@csrf_exempt
def getUser(request):
    username = request.META.get(SHIB_USER_ATTRIBUTE)
    return HttpResponse(json.dumps(User(username)))

@csrf_exempt
def getTerms(request):
    terms_markdown = open('onboarding/markdown/terms.md', 'r').read()
    return HttpResponse(markdown.markdown(terms_markdown))
