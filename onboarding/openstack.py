from django.conf import settings
from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client
from keystoneauth1.exceptions.http import NotFound



class Openstack(object):
    def __init__(self):
        self._OS_AUTHURL = getattr(settings, 'OS_AUTHURL')
        self._OS_USERNAME = getattr(settings, 'OS_USERNAME')
        self._OS_PASSWORD = getattr(settings, 'OS_PASSWORD')
        self._OS_PROJECT = getattr(settings, 'OS_PROJECT')
        self._OS_USER_DOMAIN = getattr(settings, 'OS_USER_DOMAIN')
        self._OS_PROJECT_DOMAIN = getattr(settings, 'OS_PROJECT_DOMAIN')

        self._TERMS_ROLE = getattr(settings, 'TERMS_ROLE')
        self._TERMS_DOMAIN = getattr(settings, 'TERMS_DOMAIN')

        self._USERS_DOMAIN = getattr(settings, 'USERS_DOMAIN')

        self._TRIAL_PROJECT_DOMAIN = getattr(settings, 'TRIAL_PROJECT_DOMAIN')
        self._TRIAL_PROJECT_PREFIX = getattr(settings, 'TRIAL_PROJECT_PREFIX')
        self.keystone = self._get_keystone_client()

    def _get_keystone_client(self):
        auth = v3.Password(auth_url=self._OS_AUTHURL, username=self._OS_USERNAME, password=self._OS_PASSWORD,
                            project_name=self._OS_PROJECT, user_domain_name=self._OS_USER_DOMAIN, project_domain_name=self._OS_PROJECT_DOMAIN)
        sess = session.Session(auth=auth)
        return client.Client(session=sess)

    def get_user_list(self, user):
        return self.keystone.users.list(name=user, domain=self._USERS_DOMAIN)

    def is_registered_user(self, list):
        return len(list) == 1

    def has_terms(self, user):
        role = self.keystone.roles.list(domain=self._TERMS_DOMAIN, name=self._TERMS_ROLE)[0]
        try:
            return self.keystone.roles.check(role, user=user, domain='default')
        except NotFound:
            return False

    def trial_project_exist(keystone, user):
        trial_project_name = "%s%s" % (self._TRIAL_PROJECT_PREFIX, user.name)
        trial_projects_list = self.keystone.projects.list(domain=self._TRIAL_PROJECT_DOMAIN, name=trial_project_name)
        return (len(trial_projects_list) == 1) and (trial_projects_list[0].is_trial == 'True' if hasattr(trial_projects_list[0], 'is_trial') else False)
