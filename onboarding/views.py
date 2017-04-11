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
SHIB_EMAIL_ATTRIBUTE = getattr(settings, 'SHIB_EMAIL_ATTRIBUTE')

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
    # Need to get more logic here, for institution specific terms...
    terms_markdown = open('onboarding/markdown/terms.md', 'r').read()
    return HttpResponse(markdown.markdown(terms_markdown))

@csrf_exempt
def createUser(request):
    username = request.META.get(SHIB_USER_ATTRIBUTE)
    openstack_client = Openstack(username)
    user = openstack_client.create_user_with_regex_filter(request.META.get(SHIB_EMAIL_ATTRIBUTE))

@csrf_exempt
def getWelcome(request):
    welcome_markdown = open('onboarding/markdown/welcome.md', 'r').read()
    return HttpResponse(markdown.markdown(welcome_markdown))

def getProjectList(request):
    openstack_client = Openstack()
    project_return_list = []
    for project in openstack_client.get_project_list():
        project_return_list.append({
            'Name': project.name,
            'Description': project.description,
            'ResearchField': project.researchField,
            'PrimaryInstitution': project.primaryInstitution if hasattr(project, 'primaryInstitution') else None
        })
    return HttpResponse(json.dumps(project_return_list))
