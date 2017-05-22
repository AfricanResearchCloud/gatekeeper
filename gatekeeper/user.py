from gatekeeper.openstack import Openstack
import re

class User(dict):
    def __init__(self, username):
        self['username'] = username
        openstack_client = Openstack(username)
        self['institution'] = re.search(r'\@(.+)$', username).group(1)
        self['id'] = openstack_client.get_user().id
        self['displayName'] = openstack_client.get_user().description
        self['isExists'] = openstack_client.is_registered_user()
        self['isTermsSigned'] = openstack_client.is_terms_signed()
        self['isTrialCreated'] = openstack_client.is_trial_created()
        self['isTrialCreateAllowed'] = openstack_client.is_trail_create_allowed()
        self['isCreateAllowed'] = openstack_client.is_user_create_allowed()

    def __hash__(self):
        return hash(tuple(sorted(self.items())))
