from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from gatekeeper.openstack import Openstack
from gatekeeper.utils import sendemail
import json

SHIB_USER_ATTRIBUTE = settings.SHIB_USER_ATTRIBUTE

@csrf_exempt
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
    return HttpResponse(json.dumps(project_return_list), content_type="application/json")

@csrf_exempt
def requestProjectAccess(request, project):
    username = request.META.get(SHIB_USER_ATTRIBUTE)
    openstack_client = Openstack()
    pi_email_addresses = openstack_client.get_project_pi_email(project)

    return None

@csrf_exempt
def grantProjectAccess(request, project, participant):
    return None

@csrf_exempt
def createTrialProject(request):
    return None

@csrf_exempt
def requestNewProjectAllocation(request):
    return None

@csrf_exempt
def increaseProjectAllocation(request):
    return None
