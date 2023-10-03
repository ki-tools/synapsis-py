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
        self.__from_arg_or_env__(init_args, 'configPath', 'SYNAPSE_CONFIG_FILE')
        return init_args

    def __build_login_args__(self):
        login_args = {**Synapse.__SYNAPSE_LOGIN_ARGS_DEFAULT__, **self.__synapse_login_args__}
        self.__from_arg_or_env__(login_args, 'authToken', 'SYNAPSE_AUTH_TOKEN')
        if 'authToken' not in login_args:
            self.__from_arg_or_env__(login_args, 'email', 'SYNAPSE_USERNAME')
            self.__from_arg_or_env__(login_args, 'password', 'SYNAPSE_PASSWORD')
        return login_args

    def __from_arg_or_env__(self, args, key, env_var):
        arg_value = args and args.get(key, None)
        env_value = os.environ.get(env_var, None)
        for value in [arg_value, env_value]:
            if value is not None and str(value).strip() != '':
                args[key] = value
                return value

        if key in args:
            args.pop(key)
        return None

    def __login__(self, hooks=None):
        """Login to Synapse.

        :return: None
        :raises LoginError: If logging into Synapse fails.
        """
        init_args = self.__build_init_args__()
        login_args = self.__build_login_args__()
        super().__init__(**init_args)
        try:
            self.login(**login_args)
            if hooks:
                hooks.__call_hook__(hooks.AFTER_LOGIN)
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
