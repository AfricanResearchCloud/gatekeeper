from django.conf import settings
from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client

OS_AUTHURL = getattr(settings, 'OS_AUTHURL')
OS_USERNAME = getattr(settings, 'OS_USERNAME')
OS_PASSWORD = getattr(settings, 'OS_PASSWORD')
OS_PROJECT = getattr(settings, 'OS_PROJECT')
OS_USER_DOMAIN = getattr(settings, 'OS_USER_DOMAIN')
OS_PROJECT_DOMAIN = getattr(settings, 'OS_PROJECT_DOMAIN')

TERMS_ROLE = getattr(settings, 'TERMS_ROLE')
TERMS_DOMAIN = getattr(settings, 'TERMS_DOMAIN')

class Openstack():
    def get_keystone_client():
        auth = v3.Password(auth_url=OS_AUTHURL, username=OS_USERNAME, password=OS_PASSWORD,
                            project_name=OS_PROJECT, user_domain_name=OS_USER_DOMAIN, project_domain_name=OS_PROJECT_DOMAIN)
        sess = session.Session(auth=auth)
        return client.Client(session=sess)

    def get_user_list(keystone, user):
        search_params = {
            'name': user
        }
        return keystone.users.list(**search_params)

    def is_registered_user(list):
        return len(list) == 1

    def has_terms(keystone, user):
        role_search = {'name': TERMS_ROLE }
        role = keystone.roles.list(domain=TERMS_DOMAIN, **role_search)[0]
