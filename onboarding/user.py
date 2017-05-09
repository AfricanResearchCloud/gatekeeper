from gatekeeper.openstack import Openstack

class User(dict):
    def __init__(self, username):
        self['username'] = username
        openstack_client = Openstack(username)
        self['isExists'] = openstack_client.is_registered_user()
        self['isTermsSigned'] = openstack_client.is_terms_signed()
        self['isTrialCreated'] = openstack_client.is_trial_created()
        self['isCreateAllowed'] = openstack_client.is_user_create_allowed()
