from django.conf import settings
from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client
from keystoneauth1.exceptions.http import NotFound



class Openstack(object):
    def __init__(self, username=None):
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
        return self._keystone.users.create(name=self._username, email=email, domain=self._USERS_DOMAIN)

    def create_user_with_regex_filter(self, email, regex):
        """
        Creates a new user after checking username with regex filter

        User should have been loaded first with load_user()
        :param str email: Email address to assign to user
        :param regex regex: Regex to apply to username to determine if create is allowed
        """
        if re.match(regex, self._username):
            return self._create_user(email=email)
        else:
            return False

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
        role = self._keystone.roles.list(domain=self._TERMS_DOMAIN, name=self._TERMS_ROLE)[0]
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
