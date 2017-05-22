from django.conf import settings
from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client as keystone_client
from keystoneauth1.exceptions.http import NotFound
from novaclient import client as nova_client
from cinderclient import client as cinder_client
from neutronclient import client as neutron_client
from datetime import datetime, timedelta
import re

DEFAULT_EXPIRATION_DATE = datetime.now() + timedelta(days=settings.PROJECT_EXPIRATION_DAYS)
DEFAULT_PROJECT_DOMAIN = settings.PROJECT_DOMAIN

COMPUTE_QUOTAS = {
    'cores': 'cores',
    'fixed_ips': 'fixed-ips',
    'injected_file_content_bytes': 'injected-file-size',
    'injected_file_path_bytes': 'injected-path-size',
    'injected_files': 'injected-files',
    'instances': 'instances',
    'key_pairs': 'key-pairs',
    'metadata_items': 'properties',
    'ram': 'ram',
    'server_groups': 'server-groups',
    'server_group_members': 'server-group-members',
}
VOLUME_QUOTAS = {
    'backups': 'backups',
    'backup_gigabytes': 'backup-gigabytes',
    'gigabytes': 'gigabytes',
    'per_volume_gigabytes': 'per-volume-gigabytes',
    'snapshots': 'snapshots',
    'volumes': 'volumes',
}
NOVA_NETWORK_QUOTAS = {
    'floating_ips': 'floating-ips',
    'security_group_rules': 'secgroup-rules',
    'security_groups': 'secgroups',
}
NETWORK_QUOTAS = {
    'floatingip': 'floating-ips',
    'security_group_rule': 'secgroup-rules',
    'security_group': 'secgroups',
    'network': 'networks',
    'subnet': 'subnets',
    'port': 'ports',
    'router': 'routers',
    'rbac_policy': 'rbac-policies',
    'vip': 'vips',
    'subnetpool': 'subnetpools',
    'healthmonitor': 'health-monitors',
    'l7policy': 'l7policies',
}


class Openstack(object):
    def __init__(self, username=None):
        self._OS_AUTHURL = settings.OS_AUTHURL
        self._OS_USERNAME = settings.OS_USERNAME
        self._OS_PASSWORD = settings.OS_PASSWORD
        self._OS_PROJECT = settings.OS_PROJECT
        self._OS_USER_DOMAIN = settings.OS_USER_DOMAIN
        self._OS_PROJECT_DOMAIN = settings.OS_PROJECT_DOMAIN
        self._TERMS_ROLE = settings.TERMS_ROLE
        self._TERMS_DOMAIN = settings.TERMS_DOMAIN
        self._USERS_DOMAIN = settings.USERS_DOMAIN
        self._TRIAL_PROJECT_DOMAIN = settings.TRIAL_PROJECT_DOMAIN
        self._TRIAL_PROJECT_PREFIX = settings.TRIAL_PROJECT_PREFIX
        self._USER_CREATE_REGEX = settings.USER_CREATE_REGEX
        self._PROJECT_DOMAIN = settings.PROJECT_DOMAIN
        self._PROJECT_MEMBER_ROLE = settings.PROJECT_MEMBER_ROLE
        self._PRINCIPLE_INVESTIGATOR_ROLE = settings.PRINCIPLE_INVESTIGATOR_ROLE
        self._keystone = self._get_keystone_client()
        self._nova = self._get_nova_client()
        self._cinder = self._get_cinder_client()
        self._isExists = False
        if username != None:
            self.load_user(username=username)

    def _get_session(self):
        """
        Returns a session object for use with creating clients
        """
        auth = v3.Password(auth_url=self._OS_AUTHURL, username=self._OS_USERNAME, password=self._OS_PASSWORD,
                            project_name=self._OS_PROJECT, user_domain_name=self._OS_USER_DOMAIN, project_domain_name=self._OS_PROJECT_DOMAIN)
        return session.Session(auth=auth)

    def _get_keystone_client(self):
        """
        Returns a keysone client object

        Create a keystone client object from environment variables
        """
        auth = v3.Password(auth_url=self._OS_AUTHURL, username=self._OS_USERNAME, password=self._OS_PASSWORD,
                            project_name=self._OS_PROJECT, user_domain_name=self._OS_USER_DOMAIN, project_domain_name=self._OS_PROJECT_DOMAIN)
        sess = session.Session(auth=auth)
        return keystone_client.Client(session=sess)

    def _get_nova_client(self):
        """
        Returns a nova client object
        """
        return nova_client.Client("2.1", session=self._get_session())

    def _get_cinder_client(self):
        """
        Returns a cinder client object
        """
        return cinder_client.Client("2", session=self._get_session())

    def load_user(self, username):
        """
        Loads Opestack object with user according to username

        Searches keystone for the supplied username and populates _user and _isExists accordingly.
        :param str username: the name of the user
        """
        self._isExists = False
        self._username = username
        user_list = self._keystone.users.list(name=username, domain=self._USERS_DOMAIN)
        if len(user_list) == 1:
            self._isExists = True
            self._user = user_list[0]
            return True
        else:
            return False

    def _create_user(self, email, displayName):
        """
        Creates a new user in keystone

        Create a user with the supplied name & email
        User should have been loaded first with load_user()
        :param str email: Email address to assign to user (usually loaded from environment)
        """
        user = self._keystone.users.create(name=self._username, email=email, domain=self._USERS_DOMAIN, enabled=False, description=displayName)
        self.load_user(self._username)
        return True if user else False

    def create_user_with_regex_filter(self, email, displayName):
        """
        Creates a new user after checking username with regex filter

        User should have been loaded first with load_user()
        :param str email: Email address to assign to user
        """
        if self.is_user_create_allowed:
            return self._create_user(email=email, displayName=displayName)
        else:
            return False

    def is_user_create_allowed(self):
        """
        Checks if username is allowed to be created
        """
        return True if re.search(self._USER_CREATE_REGEX, self._username) else False

    def get_user(self):
        """
        Returns the current openstack (python-keystoneclient) user object
        """
        return self._user

    def is_registered_user(self):
        """
        Returns if the user exists in keystone
        """
        return self._isExists

    def is_terms_signed(self):
        """
        Returns if the user has the TermsSigned Role assigned
        """
        if not self._isExists:
            return False
        role = self._keystone.roles.list(domain_id=self._TERMS_DOMAIN, name=self._TERMS_ROLE)[0]
        try:
            return self._keystone.roles.check(role, user=self._user, domain='default')
        except NotFound:
            return False

    def is_trial_created(self):
        """
        Returns whether the user has a trial project
        """
        if not self._isExists:
            return False
        trial_project_name = "%s%s" % (self._TRIAL_PROJECT_PREFIX, self._user.name)
        trial_projects_list = self._keystone.projects.list(domain=self._TRIAL_PROJECT_DOMAIN, name=trial_project_name)
        return (len(trial_projects_list) == 1) and (trial_projects_list[0].is_trial == 'True' if hasattr(trial_projects_list[0], 'is_trial') else False)

    def get_project_list(self):
        """
        Returns a list of projects
        """
        project_list = self._keystone.projects.list(domain=self._PROJECT_DOMAIN)
        project_return_list = []
        for project in project_list:
            if hasattr(project, 'researchField'):
                project_return_list.append(project)
        return project_return_list

    def get_project_pi_email(self, project_id):
        """
        Returns an email list of PIs for a project
        :param str project_id: ID of the project to return the pi's of
        """
        email_addresses = []
        principleInvestigators = self.get_project_pis(project_id)
        for principleInvestigator in principleInvestigators:
            if hasattr(principleInvestigator, 'email'):
                email_addresses.append(principleInvestigator.email)
        return email_addresses

    def get_project_pis(self, project_id):
         """
         Returns a list of project PIs
         :param str project_id: ID of the project to return the pi's of
         """
         role = self._keystone.roles.list(name=self._PRINCIPLE_INVESTIGATOR_ROLE, domain_id=self._PROJECT_DOMAIN)
         principleInvestigators = []
         if (len(role) == 1):
           assignments = self._keystone.role_assignments.list(role=role[0], project=project_id)
           for assignment in assignments:
              principleInvestigator = self._keystone.users.get(assignment.user['id'])
              principleInvestigators.append(principleInvestigator)
         return principleInvestigators

    def is_project_pi(self, project_id):
        """
        Returns whether the current user is a PI for the project
        :param str project_id: Name of the project to return the pi's of
        """
        project = self._keystone.projects.get(project_id)
        role = self._keystone.roles.list(name=self._PRINCIPLE_INVESTIGATOR_ROLE, domain_id=self._PROJECT_DOMAIN)
        if (len(role) == 1):
          try:
              return self._keystone.roles.check(role[0], user=self._user, project=project_id)
          except NotFound:
              return False
        return False

    def assign_project_access(self, project_id, user_id):
        """
        Assign a user to a project
        :param str project_id: The ID of the project to grant the user access to
        :param str user_id: The ID of the user to grant access to
        """
        if self.is_project_pi(project_id):
            #TODO: Assign role to user
            role = self._keystone.roles.list(name=self._PROJECT_MEMBER_ROLE)
            if (len(role) == 1):
                self._keystone.roles.grant(role[0], user=user_id, project=project_id)
                return True
            else:
                return False
        else:
            return False

    def sign_terms(self):
        """
        Assign user the signed terms role
        """
        domain = self._keystone.domains.list(name=self._TERMS_DOMAIN)
        role = self._keystone.roles.list(name=self._TERMS_ROLE, domain_id=self._TERMS_DOMAIN)
        if (len(domain) == 1) and (len(role) == 1):
            self._keystone.roles.grant(role[0], user=self._user, domain=domain[0])
            self._keystone.users.update(user=self._user, enabled=True)
        return

    def get_project(self, project_id):
        """
        Return a project from it's id
        """
        return self._keystone.projects.get(project_id)

    def get_participant_email(self, participant_id):
        """
        Returm the email address of a user based on their id
        """
        return self.get_participant(participant_id).email

    def get_participant(self, participant_id):
        """
        Return a keystone user object for the participant
        :param str participant_id: id of the user to return
        """
        return self._keystone.users.get(participant_id)

    def is_trail_project_create_allowed(self):
        """
        Returns True if the current user is allowed to create a trail project
        """
        return True if re.search(self._TRAIL_CREATE_REGEX, self._username) else False

    def create_project(self, name, description, primaryInstitution, researchField, domain=DEFAULT_PROJECT_DOMAIN ,expirationTime=DEFAULT_EXPIRATION_DATE, isTrial=True, **quota):
        """
        Creates a new project
        :param str name: Name of the project
        :param str description: Project description
        :param str primaryInstitution: The institution that is the primary contact for this project
        :param str researchField: A 6 digit code to classify the project according to CESM
        :param date expirationTime: The expiration date of the project. Will be used for project archiving and decomissioning
        :param boolean isTrial: Flag to set if it's a trail project or not.
        """
        project_domain = self._keystone.domains.list(name=domain)
        if (len(project_domain) == 1):
            project = self._keystone.projects.create(name=name, description=description, domain=project_domain[0].id, researchField=researchField, expirationTime=expirationTime, isTrial=isTrial)
            #TODO: Quota
            compute_quotas = {}
            for k, v in COMPUTE_QUOTAS.items():
                value = getattr(quota, k, None)
                if value is not None:
                    compute_quotas[k] = value
            volume_quotas = {}
            for k,v in VOLUME_QUOTAS.items():
                value = getattr(quota, k, None)
                if value is not None:
                    volume_quotas[k] = value
            network_quotas = {}
            if len(self._keystone.services.list(type='network')) > 0:
                for k,v in NETWORK_QUOTAS.items():
                    value = getattr(quota, k, None)
                    if value is not None:
                        network_quotas[k] = value
            else:
                for k,v in NOVA_NETWORK_QUOTAS.items():
                    value = getattr(quota, k, None)
                    if value is not None:
                        compute_quotas[k] = value
            if compute_quotas:
                self._nova.quotas.update(project, compute_quotas)
            if volume_quotas:
                self._cinder.quotas.update(project, volume_quotas)
            if network_quotas:
                self._neutron.
        else:
            return False
