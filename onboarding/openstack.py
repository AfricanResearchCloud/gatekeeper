from django.conf import settings
from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client
from keystoneauth1.exceptions.http import NotFound

OS_AUTHURL = getattr(settings, 'OS_AUTHURL')
OS_USERNAME = getattr(settings, 'OS_USERNAME')
OS_PASSWORD = getattr(settings, 'OS_PASSWORD')
OS_PROJECT = getattr(settings, 'OS_PROJECT')
OS_USER_DOMAIN = getattr(settings, 'OS_USER_DOMAIN')
OS_PROJECT_DOMAIN = getattr(settings, 'OS_PROJECT_DOMAIN')

TERMS_ROLE = getattr(settings, 'TERMS_ROLE')
TERMS_DOMAIN = getattr(settings, 'TERMS_DOMAIN')

USERS_DOMAIN = getattr(settings, 'USERS_DOMAIN')

TRIAL_PROJECT_DOMAIN = getattr(settings, 'TRIAL_PROJECT_DOMAIN')
TRIAL_PROJECT_PREFIX = getattr(settings, 'TRIAL_PROJECT_PREFIX')

class Openstack():
    def get_keystone_client():
        auth = v3.Password(auth_url=OS_AUTHURL, username=OS_USERNAME, password=OS_PASSWORD,
                            project_name=OS_PROJECT, user_domain_name=OS_USER_DOMAIN, project_domain_name=OS_PROJECT_DOMAIN)
        sess = session.Session(auth=auth)
        return client.Client(session=sess)

    def get_user_list(keystone, user):
        return keystone.users.list(name=user, domain=USERS_DOMAIN)

    def is_registered_user(list):
        return len(list) == 1

    def has_terms(keystone, user):
        role = keystone.roles.list(domain=TERMS_DOMAIN, name=TERMS_ROLE)[0]
        try:
            return keystone.roles.check(role, user=user, domain='default')
        except NotFound:
            return False

    def trial_project_exist(keystone, user):
        trial_project_name = "%s%s" % (TRIAL_PROJECT_PREFIX, user.name)
        trial_projects_list = keystone.projects.list(domain=TRIAL_PROJECT_DOMAIN, name=trial_project_name)
        return (len(trial_projects_list) == 1) and (trial_projects_list[0].is_trial == 'True' if hasattr(trial_projects_list[0], 'is_trial') else False)
