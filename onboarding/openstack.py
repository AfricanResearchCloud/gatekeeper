from django.conf import settings
from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client
from keystoneauth1.exceptions.http import NotFound
import re


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
        self._PRINCIPLE_INVESTIGATOR_ROLE = settings.PRINCIPLE_INVESTIGATOR_ROLE
        self._keystone = self._get_keystone_client()
        self._isExists = False
        if username != None:
            self.load_user(username=username)


    def _get_keystone_client(self):
        """
        Returns a keysone client object

        Create a keystone client object from environment variables
        """
        auth = v3.Password(auth_url=self._OS_AUTHURL, username=self._OS_USERNAME, password=self._OS_PASSWORD,
                            project_name=self._OS_PROJECT, user_domain_name=self._OS_USER_DOMAIN, project_domain_name=self._OS_PROJECT_DOMAIN)
        sess = session.Session(auth=auth)
        return client.Client(session=sess)

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

    def _create_user(self, email):
        """
        Creates a new user in keystone

        Create a user with the supplied name & email
        User should have been loaded first with load_user()
        :param str email: Email address to assign to user (usually loaded from environment)
        """
        user = self._keystone.users.create(name=self._username, email=email, domain=self._USERS_DOMAIN, enabled=False)
        self.load_user(self._username)
        return True if user else False

    def create_user_with_regex_filter(self, email):
        """
        Creates a new user after checking username with regex filter

        User should have been loaded first with load_user()
        :param str email: Email address to assign to user
        """
        if self.is_user_create_allowed:
            return self._create_user(email=email)
        else:
            return False

    def is_user_create_allowed(self):
        """
        Checks if username is allowed to be created
        """
        return True if re.match(self._USER_CREATE_REGEX, self._username) else False

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

    def get_project_pi_email(self, project_name):
        """
        Returns an email list of PIs for a project
        :param str project_name: Name of the project to return the pi's of
        """
        project = self._keystone.projects.list(name=project_name, domain=self._PROJECT_DOMAIN)
        role = self._keystone.roles.list(name=self._PRINCIPLE_INVESTIGATOR_ROLE, domain_id=self._PROJECT_DOMAIN)
        email_addresses = []
        if (len(project) == 1) and (len(role) == 1):
            assignments = self._keystone.role_assignments.list(role=role[0], project=project[0])
            for assignment in assignments:
                PrincipleInvestigator = self._keystone.users.get(assignment.user['id'])
                if hasattr(PrincipleInvestigator, 'email'):
                    email_addresses.append(PrincipleInvestigator.email)
        return email_addresses

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
