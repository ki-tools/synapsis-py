import typing as t
import argparse


def inject(arg_parser: argparse.ArgumentParser) -> None:
    arg_parser.add_argument('-u', '--username', help='Synapse username.', default=None)
    arg_parser.add_argument('-p', '--password', help='Synapse password.', default=None)
    arg_parser.add_argument('--auth-token', help='Synapse auth token.', default=None)
    arg_parser.add_argument('--synapse-config', help='Path to Synapse configuration file.', default=None)


def configure(parsed_args: argparse.Namespace,
              login: t.Optional[bool] = False,
              synapse_args: t.Optional[dict] = {},
              login_args: t.Optional[dict] = {}
              ) -> None:
    from .. import Synapsis
    _synapse_args = {
        'configPath': parsed_args.synapse_config
    }
    if synapse_args:
        _synapse_args.update(synapse_args)

    _login_args = {
        'email': parsed_args.username,
        'password': parsed_args.password,
        'authToken': parsed_args.auth_token
    }
    if login_args:
        _login_args.update(login_args)

    Synapsis.configure(synapse_args=_synapse_args, **_login_args)
    if login:
        Synapsis.login()
