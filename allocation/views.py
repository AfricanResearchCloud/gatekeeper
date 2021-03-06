from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from gatekeeper.openstack import Openstack
from gatekeeper.user import User
from gatekeeper.utils import sendemail
from gatekeeper.project import Project
from django.template import loader
import json
import logging

LOG = logging.getLogger(__name__)
SHIB_USER_ATTRIBUTE = settings.SHIB_USER_ATTRIBUTE
ALLOCATIONS_EMAIL = settings.ALLOCATIONS_EMAIL
APPLICATION_BASE_URL = settings.APPLICATION_BASE_URL

@csrf_exempt
def getProjectList(request):
    openstack_client = Openstack()
    project_return_list = []
    for project in openstack_client.get_project_list():
        project_return_list.append(Project(project))
    return HttpResponse(json.dumps(project_return_list), content_type="application/json")

@csrf_exempt
def requestProjectAccess(request, project_id):
    username = request.META.get(SHIB_USER_ATTRIBUTE)
    openstack_client = Openstack()
    pi_email_addresses = openstack_client.get_project_pi_email(project_id)
    openstack_project = openstack_client.get_project(project_id)
    LOG.info("User %s is requesting access to %s, emailing: %s" %(username, project_id, ','.join(pi_email_addresses)))
    email_content = loader.get_template("project_access_request.html").render({
        'title': 'Requesting Project Access',
        'participant': User(username),
        'project': Project(openstack_project),
        'applicationUrl': APPLICATION_BASE_URL
    })
    LOG.info(email_content)
    sendemail(pi_email_addresses, ALLOCATIONS_EMAIL, "Project Access Request - %s" % (openstack_project.name), email_content)
    return HttpResponse(json.dumps({'success': True}), content_type="application/json")

@csrf_exempt
def grantProjectAccess(request, project_id, participant):
    username = request.META.get(SHIB_USER_ATTRIBUTE)
    openstack_client = Openstack(username)
    if openstack_client.is_project_pi(project_id):
        openstack_client.assign_project_access(project_id, participant)
        LOG.info("Assigning access to %s for %s by %s" % (participant, project_id, openstack_client.get_user().id))
        openstack_project = openstack_client.get_project(project_id)
        pi_email_addresses = openstack_client.get_project_pi_email(project_id)
        op_participant = User(openstack_client.get_participant(participant).name)
        op_project = Project(openstack_project)
        op_user = User(username)
        email_content = loader.get_template("project_access_granted.html").render({
            'title': 'Project Access Granted',
            'participant': op_participant,
            'project': op_project,
            'user': op_user
        })
        sendemail(pi_email_addresses, ALLOCATIONS_EMAIL, "Project Access Granted", email_content)
        pi_email_content = loader.get_template("project_access_granted_pi.html").render({
            'title': 'Project Access Granted',
            'participant': op_participant,
            'project': op_project,
            'user': op_user
        })
        sendemail([openstack_client.get_participant_email(participant)], ALLOCATIONS_EMAIL, "Project Access Approved", pi_email_content, pi_email_addresses)
        return HttpResponse(json.dumps({'success': True}), content_type="application/json")
    LOG.info("Not project PI")
    return HttpResponse(json.dumps({'success': False}), content_type="application/json")

@csrf_exempt
def createTrialProject(request):
    username = request.META.get(SHIB_USER_ATTRIBUTE)

    return None

@csrf_exempt
def requestNewProjectAllocation(request):
    return None

@csrf_exempt
def increaseProjectAllocation(request):
    return None
