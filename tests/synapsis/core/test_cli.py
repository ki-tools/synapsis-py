import pytest
import argparse
from synapsis import Synapsis, cli
from synapsis.core import Utils, exceptions


def new_parser():
    parser = argparse.ArgumentParser()
    cli.inject(parser)
    return parser


def test_it_injects_args():
    parser = new_parser()
    for name in ['--username', '--password', '--auth-token', '--synapse-config']:
        action = Utils.find(parser._actions, lambda a: name in a.option_strings)
        assert action is not None


def test_it_configures_from_args(syn_test_credentials, syn_test_auth_token, synapse_test_config,
                                 clear_env_vars, set_env_vars):
    test_username, test_password = syn_test_credentials

    def reset():
        clear_env_vars()
        Synapsis.configure()
        assert Synapsis.logged_in() is False
        assert Synapsis.Synapse.__synapse_init_args__ == {}
        assert Synapsis.Synapse.__synapse_login_args__ == {}

    reset()
    parser = new_parser()
    args = parser.parse_args([])
    cli.configure(args)
    assert Synapsis.logged_in() is False
    with pytest.raises(exceptions.LoginError):
        Synapsis.login()
    ###########################################################################
    # User/Pass
    ###########################################################################
    args = parser.parse_args(['--username', test_username, '--password', test_password])
    cli.configure(args)
    assert Synapsis.logged_in() is False
    Synapsis.login()
    assert Synapsis.logged_in() is True

    reset()
    cli.configure(args, login=True)
    assert Synapsis.logged_in() is True

    # ENV Vars
    reset()
    set_env_vars(username=test_username, password=test_password)
    args = parser.parse_args([])
    cli.configure(args)
    assert Synapsis.logged_in() is False
    Synapsis.login()
    assert Synapsis.logged_in() is True

    reset()
    set_env_vars(username=test_username, password=test_password)
    cli.configure(args, login=True)
    assert Synapsis.logged_in() is True

    ###########################################################################
    # Auth Token
    ###########################################################################
    reset()
    args = parser.parse_args(['--auth-token', syn_test_auth_token])
    cli.configure(args)
    assert Synapsis.logged_in() is False
    Synapsis.login()
    assert Synapsis.logged_in() is True

    reset()
    cli.configure(args, login=True)
    assert Synapsis.logged_in() is True

    # ENV Vars
    reset()
    set_env_vars(auth_token=syn_test_auth_token)
    args = parser.parse_args([])
    cli.configure(args)
    assert Synapsis.logged_in() is False
    Synapsis.login()
    assert Synapsis.logged_in() is True

    reset()
    set_env_vars(auth_token=syn_test_auth_token)
    cli.configure(args, login=True)
    assert Synapsis.logged_in() is True

    ###########################################################################
    # Synapse Config File
    ###########################################################################
    reset()
    config_path = synapse_test_config(username=test_username, password=test_password, auth_token=syn_test_auth_token)
    args = parser.parse_args(['--synapse-config', config_path])
    cli.configure(args)
    assert Synapsis.logged_in() is False
    Synapsis.login()
    assert Synapsis.logged_in() is True

    reset()
    cli.configure(args, login=True)
    assert Synapsis.logged_in() is True

    # ENV Vars
    reset()
    set_env_vars(config_file=config_path)
    args = parser.parse_args([])
    cli.configure(args)
    assert Synapsis.logged_in() is False
    Synapsis.login()
    assert Synapsis.logged_in() is True

    reset()
    set_env_vars(config_file=config_path)
    cli.configure(args, login=True)
    assert Synapsis.logged_in() is True
