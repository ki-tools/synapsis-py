import pytest
from synapsis import Synapsis
from synapsis.core import Synapsis as SynapsisClass, SynapsisUtils, exceptions, Utils as _Utils
from synapsis.synapse import Synapse, SynapseUtils
from synapsis.synapse.synapse_utils import SynapseutilsAttrWrapper
import synapseclient


def all_items_match(items, attr=None):
    if attr is not None:
        items = [getattr(item, attr) for item in items]
    return all(ele == items[0] for ele in items)


def assert_match(items, is_a=None, equals=None):
    assert all_items_match(items)
    if is_a is not None:
        for item in items:
            assert isinstance(item, is_a)
    if equals is not None:
        if callable(equals):
            assert equals(items)
        else:
            for item in items:
                assert item == equals


def assert_is_logged_in():
    assert Synapsis.Synapse.credentials is not None
    if hasattr(Synapsis.Synapse, '_loggedIn'):
        assert Synapsis.Synapse._loggedIn() is not False
    else:
        assert Synapsis.Synapse._is_logged_in() is True


def assert_is_logged_out():
    assert Synapsis.Synapse.credentials is None
    if hasattr(Synapsis.Synapse, '_loggedIn'):
        assert Synapsis.Synapse._loggedIn() is False
    else:
        assert Synapsis.Synapse._is_logged_in() is False


def test_configure(synapse_test_helper, test_credentials, other_test_credentials, synapse_test_config,
                   clear_env_vars, set_env_vars):
    test_username, test_password, test_auth_token = test_credentials
    other_test_username, other_test_password, other_test_auth_token = other_test_credentials

    def reset():
        clear_env_vars()
        Synapsis.configure()
        assert Synapsis.logged_in() is False
        assert Synapsis.Synapse.__synapse_init_args__ == {}
        assert Synapsis.Synapse.__synapse_login_args__ == {}

    def assert_login(*args, _username: str, **kwargs):
        assert Synapsis.logged_in() is False
        Synapsis.configure(*args, **kwargs)
        assert Synapsis.Synapse.__config__ == {}
        assert Synapsis.login()
        assert Synapsis.logged_in()
        assert Synapsis.Synapse.__synapse_init_args__ == {}
        assert Synapsis.Synapse.__synapse_login_args__ == {}
        assert Synapsis.Synapse.credentials.username == _username
        assert Synapsis.Synapse.__config__ != {}

    # Failed login
    reset()
    with pytest.raises(exceptions.LoginError):
        Synapsis.login()

    # User/Pass.
    reset()
    assert_login(email=other_test_username, password=other_test_password, _username=other_test_username)

    # User/Pass/Auth Token.
    reset()
    assert_login(email=other_test_username, password=other_test_password, authToken=other_test_auth_token,
                 _username=other_test_username)

    # User/Auth Token.
    reset()
    assert_login(email=other_test_username, authToken=other_test_auth_token, _username=other_test_username)

    # Auth Token.
    reset()
    assert_login(authToken=other_test_auth_token, _username=other_test_username)

    # ENV Vars User/Pass.
    reset()
    set_env_vars(username=other_test_username, password=other_test_password)
    assert_login(_username=other_test_username)

    # ENV Vars User/Pass/Auth Token.
    reset()
    set_env_vars(username=other_test_username, password=other_test_password, auth_token=other_test_auth_token)
    assert_login(_username=other_test_username)

    # ENV Vars Auth Token.
    reset()
    set_env_vars(auth_token=other_test_auth_token)
    assert_login(_username=other_test_username)

    # Config file User/Pass.
    reset()
    config_path = synapse_test_config(username=other_test_username, password=other_test_password)
    assert_login(synapse_args={'configPath': config_path}, _username=other_test_username)
    assert Synapsis.Synapse.configPath == config_path
    reset()
    set_env_vars(config_file=config_path)
    assert_login(_username=other_test_username)
    assert Synapsis.Synapse.configPath == config_path

    # Config file User/Pass/Auth Token.
    reset()
    config_path = synapse_test_config(username=other_test_username, password=other_test_password,
                                      auth_token=other_test_auth_token)
    assert_login(synapse_args={'configPath': config_path}, _username=other_test_username)
    reset()
    set_env_vars(config_file=config_path)
    assert_login(_username=other_test_username)

    # Config file Auth Token.
    reset()
    config_path = synapse_test_config(auth_token=test_auth_token)
    assert_login(synapse_args={'configPath': config_path}, _username=test_username)
    reset()
    set_env_vars(config_file=config_path)
    assert_login(_username=test_username)

    # Synapse Custom Config:
    #   - multi_threaded
    reset()
    assert_login(authToken=test_auth_token, _username=test_username)
    assert Synapsis.Synapse.multi_threaded is False

    reset()
    config_path = synapse_test_config(auth_token=test_auth_token)
    assert_login(synapse_args={'configPath': config_path, 'multi_threaded': False}, _username=test_username)
    assert Synapsis.Synapse.multi_threaded is False

    reset()
    assert_login(authToken=test_auth_token, synapse_args={'multi_threaded': True}, _username=test_username)
    assert Synapsis.Synapse.multi_threaded is True

    reset()
    assert_login(authToken=test_auth_token, synapse_args={'multi_threaded': False}, _username=test_username)
    assert Synapsis.Synapse.multi_threaded is False

    # Login Hooks
    reset()
    callbacks = []
    assert len(Synapsis.hooks.__hooks__) == 0
    Synapsis.hooks.after_login(lambda hook: callbacks.append(1))
    Synapsis.hooks.after_login(lambda hook: callbacks.append(2))
    assert_login(authToken=test_auth_token, _username=test_username)
    assert callbacks == [1, 2]

    # Does not call AFTER_LOGIN if logging in fails.
    reset()
    assert len(Synapsis.hooks.__hooks__[Synapsis.hooks.AFTER_LOGIN]) == 2
    callbacks = []
    with pytest.raises(exceptions.LoginError):
        Synapsis.login()
    assert callbacks == []

    Synapsis.hooks.clear()
    assert len(Synapsis.hooks.__hooks__) == 0


async def test_it_routes_to_self(synapse_test_helper):
    assert isinstance(Synapsis, SynapsisClass)
    assert Synapsis.logged_in.__self__ == Synapsis
    items = [
        Synapsis.logged_in(),
        await Synapsis.Chain.logged_in()
    ]
    assert_match(items, equals=True)

    assert Synapsis.Chain.logged_in().Result() is True


async def test_it_routes_to_synapsis_utils(synapse_test_helper, syn_project):
    assert isinstance(Synapsis.Utils, SynapsisUtils)
    assert Synapsis.Utils.find_entity.__self__ == Synapsis.Utils
    assert Synapsis.Utils.__synapse__ == Synapsis.Synapse
    items = [
        Synapsis.Utils.find_entity(syn_project.name),
        await Synapsis.Chain.Utils.find_entity(syn_project.name)
    ]
    assert_match(items, equals=syn_project)


async def test_it_routes_to_synapse(synapse_test_helper):
    assert isinstance(Synapsis.Synapse, Synapse)
    assert Synapsis.Synapse.getUserProfile.__self__ == Synapsis.Synapse
    assert Synapsis.getUserProfile.__self__ == Synapsis.Synapse
    items = [
        Synapsis.getUserProfile(),
        await Synapsis.Chain.getUserProfile(),

        Synapsis.Synapse.getUserProfile(),
        await Synapsis.Chain.Synapse.getUserProfile()
    ]
    assert_match(items, equals=synapse_test_helper.client().getUserProfile())


async def test_it_routes_to_synapse_utils(synapse_test_helper):
    assert isinstance(Synapsis.SynapseUtils, SynapseUtils)
    assert isinstance(Synapsis.SynapseUtils.with_progress_bar, SynapseutilsAttrWrapper)
    assert Synapsis.SynapseUtils.__synapse__ == Synapsis.Synapse
    assert Synapsis.SynapseUtils.with_progress_bar(lambda: None, 1).__module__ == 'synapseutils.monitor'
    items = [
        Synapsis.SynapseUtils.with_progress_bar(lambda: None, 1),
        await Synapsis.Chain.SynapseUtils.with_progress_bar(lambda: None, 1),
    ]
    assert all_items_match(items, attr='__module__')


async def test_it_routes_to_utils():
    assert Synapsis.utils == _Utils
    numbers = [1, 2, 3]
    items = [
        Synapsis.utils.first(numbers),
        await Synapsis.Chain.utils.first(numbers)
    ]
    assert_match(items, equals=1)


async def test_generators(synapse_test_helper, syn_project, syn_folder, syn_folder2):
    children = list(Synapsis.Synapse.getChildren(syn_project))
    assert set([c['id'] for c in children]) == set([syn_folder.id, syn_folder2.id])

    children = [i async for i in Synapsis.Chain.Synapse.getChildren(syn_project)]
    assert set([c['id'] for c in children]) == set([syn_folder.id, syn_folder2.id])


async def test_missing_methods(synapse_test_helper):
    with pytest.raises(AttributeError):
        Synapsis.NOPE()
    with pytest.raises(AttributeError):
        await Synapsis.Chain.NOPE()

    with pytest.raises(AttributeError):
        Synapsis.Utils.NOPE()
    with pytest.raises(AttributeError):
        await Synapsis.Chain.Utils.NOPE()

    with pytest.raises(AttributeError):
        Synapsis.Synapse.NOPE()
    with pytest.raises(AttributeError):
        await Synapsis.Chain.Synapse.NOPE()

    with pytest.raises(AttributeError):
        Synapsis.Synapse.Utils.NOPE()
    with pytest.raises(AttributeError):
        await Synapsis.Chain.Synapse.Utils.NOPE()

    with pytest.raises(AttributeError):
        Synapsis.SynapseUtils.NOPE()
    with pytest.raises(AttributeError):
        await Synapsis.Chain.SynapseUtils.NOPE()


async def test_logged_in():
    assert Synapsis.logged_in() is True
    assert_is_logged_in()
    Synapsis.logout()
    assert_is_logged_out()


async def test_logout():
    assert_is_logged_in()
    Synapsis.logout()
    assert_is_logged_out()


def test_is_synapse_id():
    for id in [None, '', ' ', 'syn', 'synA', 'ssyn123', 'syn123z']:
        assert Synapsis.is_synapse_id(id) is False

    for id in ['syn123', 'SyN123', ' sYn123 ']:
        assert Synapsis.is_synapse_id(id) is True


def test_id_of():
    assert Synapsis.id_of('syn123') == 'syn123'
    assert Synapsis.id_of(synapseclient.Project(id='syn123')) == 'syn123'
