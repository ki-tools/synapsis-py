from __future__ import annotations
import typing as t
import os
import synapseclient
from synapseclient.core.exceptions import SynapseError
from ..core.exceptions import LoginError


class Synapse(synapseclient.Synapse):
    __SYNAPSE_INIT_ARGS_DEFAULT__: t.ClassVar[t.Final[dict]] = {'skip_checks': True, 'silent': True}
    __SYNAPSE_LOGIN_ARGS_DEFAULT__: t.ClassVar[t.Final[dict]] = {'silent': True, 'rememberMe': False, 'forced': True}
    __synapse_init_args__: dict = {}
    __synapse_login_args__: dict = {}

    def __init__(self, **kwargs):
        init_args = self.__build_init_args__()
        init_args.update(kwargs)
        super().__init__(**init_args)

    def __configure__(self, synapse_args: dict = {}, **login_args: dict):
        """Sets configuration options for the synapseclient and logs out.

        :param synapse_args: Args for creating the synapsecleint.Synapse instance.
        :param login_args: Args for logging into Synapse.
        :return: None
        """
        self.__synapse_init_args__ = synapse_args or {}
        self.__synapse_login_args__ = login_args or {}
        self.logout()

    def __build_init_args__(self):
        init_args = {**Synapse.__SYNAPSE_INIT_ARGS_DEFAULT__, **self.__synapse_init_args__}
        init_args['configPath'] = init_args.get('configPath', None) or os.environ.get('SYNAPSE_CONFIG_FILE', None)
        if init_args['configPath'] is None:
            init_args.pop('configPath')
        return init_args

    def __build_login_args__(self):
        login_args = {**Synapse.__SYNAPSE_LOGIN_ARGS_DEFAULT__, **self.__synapse_login_args__}
        login_args['email'] = login_args.get('email', None) or os.environ.get('SYNAPSE_USERNAME', None)
        login_args['password'] = login_args.get('password', None) or os.environ.get('SYNAPSE_PASSWORD', None)
        login_args['authToken'] = login_args.get('authToken', None) or os.environ.get('SYNAPSE_AUTH_TOKEN', None)
        return login_args

    def __login__(self):
        """Login to Synapse.

        :return: None
        :raises LoginError: If logging into Synapse fails.
        """
        init_args = self.__build_init_args__()
        login_args = self.__build_login_args__()
        super().__init__(**init_args)
        try:
            self.login(**login_args)
        except SynapseError as ex:
            raise LoginError(ex)
        self.__synapse_init_args__ = {}
        self.__synapse_login_args__ = {}

    def __logged_in__(self) -> bool:
        """Gets if the synapseclient is logged into Synapse.

        :return: True or False
        """
        if hasattr(self, '_is_logged_in'):
            return self._is_logged_in()
        else:
            return self._loggedIn() is not False
