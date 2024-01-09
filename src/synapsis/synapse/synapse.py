from __future__ import annotations
import typing as t
import os
import tempfile
import synapseclient
from synapseclient.core.exceptions import SynapseError
from ..core.exceptions import LoginError


class Synapse(synapseclient.Synapse):
    __SYNAPSE_INIT_ARGS_DEFAULT__: t.ClassVar[t.Final[dict]] = {
        'skip_checks': True,
        'silent': True,
        "multi_threaded": False
    }
    __SYNAPSE_LOGIN_ARGS_DEFAULT__: t.ClassVar[t.Final[dict]] = {
        'silent': True,
        'rememberMe': False,
        'forced': True
    }
    __CONFIG_DEFAULT__: t.ClassVar[t.Final[dict]] = {
        "multi_threaded": __SYNAPSE_INIT_ARGS_DEFAULT__['multi_threaded']
    }
    __synapse_init_args__: dict = {}
    __synapse_login_args__: dict = {}
    __config__: dict = {}

    def __init__(self, **kwargs):
        self.__init_self__(init_kwargs=kwargs)

    def __init_self__(self, init_kwargs: dict):
        init_kwargs = self.__build_init_args__(init_kwargs=init_kwargs)
        super().__init__(**init_kwargs)
        self.multi_threaded = self.__config__.get('multi_threaded', self.__CONFIG_DEFAULT__['multi_threaded'])

    def __configure__(self, synapse_args: dict = {}, **login_args: dict):
        """Sets configuration options for the synapseclient and logs out.

        :param synapse_args: Args for creating the synapseclient.Synapse instance.
        :param login_args: Args for logging into Synapse.
        :return: None
        """
        self.__synapse_init_args__ = synapse_args or {}
        self.__synapse_login_args__ = login_args or {}
        self.__config__ = {}
        self.logout()

    def __build_init_args__(self, init_kwargs: dict):
        init_args = {**Synapse.__SYNAPSE_INIT_ARGS_DEFAULT__, **init_kwargs}
        self.__from_arg_or_env__(init_args, 'configPath', 'SYNAPSE_CONFIG_FILE')

        # Pull out custom Synapse args.
        for attr, value in Synapse.__CONFIG_DEFAULT__.items():
            if attr in init_args:
                value = init_args.pop(attr)
            self.__config__[attr] = value

        if 'cache_root_dir' not in init_args:
            cache_root_dir = os.path.expandvars(os.path.expanduser((synapseclient.core.cache.CACHE_ROOT_DIR)))
            if not os.access(cache_root_dir, os.W_OK):
                init_args['cache_root_dir'] = tempfile.mkdtemp(prefix='synapseCache-')

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
        self.__init_self__(init_kwargs=self.__synapse_init_args__)
        login_args = self.__build_login_args__()
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
