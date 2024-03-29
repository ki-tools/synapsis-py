import pytest
import os
import tempfile
import shutil
import synapseclient as syn
from synapseclient.core.exceptions import SynapseHTTPError
from synapseclient.core.utils import id_of
from dotenv import load_dotenv
from synapse_test_helper import SynapseTestHelper
from synapsis import Synapsis
from synapsis.core import Utils

load_dotenv(override=True)


def _set_env_vars(username=None, password=None, auth_token=None, config_file=None):
    for key, value in [['SYNAPSE_USERNAME', username],
                       ['SYNAPSE_PASSWORD', password],
                       ['SYNAPSE_AUTH_TOKEN', auth_token],
                       ['SYNAPSE_CONFIG_FILE', config_file]
                       ]:
        if not value:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


def _clear_env_vars():
    _set_env_vars()
    for key in ['SYNAPSE_USERNAME', 'SYNAPSE_PASSWORD', 'SYNAPSE_AUTH_TOKEN', 'SYNAPSE_CONFIG_FILE']:
        assert key not in os.environ.keys()


@pytest.fixture(autouse=True)
def clear_env_vars():
    _clear_env_vars()
    yield _clear_env_vars
    _clear_env_vars()


@pytest.fixture
def set_env_vars():
    _clear_env_vars()
    yield _set_env_vars
    _clear_env_vars()


@pytest.fixture(scope='session')
def test_credentials():
    result = [
        os.environ.get('TEST_SYNAPSE_USERNAME'),
        os.environ.get('TEST_SYNAPSE_PASSWORD'),
        os.environ.get('TEST_SYNAPSE_AUTH_TOKEN')
    ]
    if None in result:
        raise Exception(
            'Environment variables not set: TEST_SYNAPSE_USERNAME, TEST_SYNAPSE_PASSWORD, or TEST_SYNAPSE_AUTH_TOKEN')
    return result


@pytest.fixture(scope='session')
def other_test_credentials():
    result = [
        os.environ.get('TEST_SYNAPSE_OTHER_USERNAME'),
        os.environ.get('TEST_SYNAPSE_OTHER_PASSWORD'),
        os.environ.get('TEST_SYNAPSE_OTHER_AUTH_TOKEN')
    ]
    if None in result:
        raise Exception(
            'Environment variables not set: TEST_SYNAPSE_OTHER_USERNAME, TEST_SYNAPSE_OTHER_PASSWORD, or TEST_SYNAPSE_OTHER_AUTH_TOKEN')
    return result


@pytest.fixture(autouse=True)
def login(test_credentials, clear_env_vars):
    clear_env_vars()
    syn_user, syn_pass, syn_auth_token = test_credentials
    if not Synapsis.logged_in() or Synapsis.Synapse.credentials.username != syn_user:
        assert Synapsis.configure(authToken=syn_auth_token).login().logged_in()
    assert Synapsis.Synapse.credentials.username == syn_user
    yield Synapsis


@pytest.fixture
def test_user(synapse_test_helper, test_credentials):
    username = test_credentials[0]
    user = synapse_test_helper.client().getUserProfile(id=username)
    return user


@pytest.fixture(scope='session')
def other_test_user(synapse_test_helper, other_test_credentials):
    other_username = other_test_credentials[0]
    other_user = synapse_test_helper.client().getUserProfile(id=other_username)
    return other_user


@pytest.fixture(scope='session')
def synapse_test_helper(test_credentials):
    if not SynapseTestHelper.configured():
        auth_token = test_credentials[2]
        synapse_client = syn.Synapse(skip_checks=True, silent=True, configPath='')
        synapse_client.login(authToken=auth_token, silent=True, rememberMe=False, forced=True)
        assert SynapseTestHelper.configure(synapse_client)

    with SynapseTestHelper() as sth:
        yield sth


@pytest.fixture(scope='session')
def synapse_test_config():
    """
    Creates a temporary Synapse config file with the test credentials and redirects
    the Synapse client to the temp config file.
    :return:
    """
    paths = []

    def _mk(username=None, password=None, auth_token=None, cache_path=None):
        cache_path = tempfile.mkdtemp() if not cache_path else cache_path
        config = ['[authentication]']
        if username:
            config.append('username = {0}'.format(username))
        if password:
            config.append('password = {0}'.format(password))
        if auth_token:
            config.append('authtoken = {0}'.format(auth_token))

        config.append('[cache]')
        config.append('location = {0}'.format(cache_path))

        config = "\n".join(config)
        fd, tmp_filename = tempfile.mkstemp(suffix='.synapseConfig')
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(config)
        paths.append(tmp_filename)
        paths.append(cache_path)
        return tmp_filename

    yield _mk

    for path in paths:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)


@pytest.fixture(scope='module')
def syn_project(synapse_test_helper):
    yield synapse_test_helper.create_project()


@pytest.fixture(scope='module')
def syn_folder(synapse_test_helper, syn_project):
    yield synapse_test_helper.create_folder(parent=syn_project)


@pytest.fixture(scope='module')
def syn_folder2(synapse_test_helper, syn_project):
    yield synapse_test_helper.create_folder(parent=syn_project)


@pytest.fixture(scope='module')
def syn_file(synapse_test_helper, syn_folder):
    yield synapse_test_helper.create_file(parent=syn_folder)


@pytest.fixture
def invite_to_team_and_accept(other_test_user, other_test_credentials, accept_team_invite, is_invited_to_team,
                              is_on_team):
    def _m(team):
        Synapsis.Utils.invite_to_team(team, other_test_user)
        assert is_invited_to_team(team, other_test_user)
        assert is_on_team(team, other_test_user) is False

        auth_token = other_test_credentials[2]
        accept_team_invite(team, other_test_user, authToken=auth_token)
        assert is_invited_to_team(team, other_test_user) is False
        assert is_on_team(team, other_test_user)

    yield _m


@pytest.fixture()
def is_on_team(synapse_test_helper):
    def _m(team, user):
        user_id = id_of(user)
        team_user_ids = list(
            map(lambda item: id_of(item.get('member')), synapse_test_helper.client().getTeamMembers(team))
        )
        return user_id in team_user_ids

    yield _m


@pytest.fixture()
def is_invited_to_team(synapse_test_helper):
    def _m(team, invitee):
        team_id = id_of(team)
        invitee = id_of(invitee)
        invites = synapse_test_helper.client().restGET('/team/{0}/openInvitation'.format(team_id)).get('results', [])
        is_invited = Utils.find(invites, lambda i: i.get('inviteeEmail', str(i.get('inviteeId', None))) == str(invitee))
        return is_invited is not None

    yield _m


@pytest.fixture()
def is_manager_on_team(synapse_test_helper):
    def _m(team, user):
        team_id = id_of(team)
        user_id = id_of(user)
        acl = synapse_test_helper.client().restGET('/team/{0}/acl'.format(team_id)).get('resourceAccess', [])
        current_access = Utils.find(acl, lambda a: str(a['principalId']) == str(user_id))
        return acl is not None and current_access is not None and \
            set(current_access['accessType']) == set(Synapsis.Permissions.TEAM_MANAGER.access_types)

    yield _m


@pytest.fixture()
def accept_team_invite(synapse_test_helper):
    def _m(team, user, **login_args):
        """
            Accepting an invite must be done as the user the invite was sent to.
            This requires login args for the invited user.
        """
        team_id = id_of(team)
        user_id = id_of(user)
        client = syn.Synapse(skip_checks=True, silent=True)
        client.login(**login_args)
        client.restPUT('/team/{0}/member/{1}'.format(team_id, user_id))
        return True

    yield _m


@pytest.fixture
def has_permission_to(synapse_test_helper):
    def _m(entity, principal, access_types=None):
        principal_id = syn.core.utils.id_of(principal)
        current_access_types = synapse_test_helper.client().getPermissions(entity, principalId=principal_id)
        if access_types is None:
            return len(current_access_types) > 0
        else:
            return set(current_access_types) == set(access_types)

    yield _m


@pytest.fixture
def has_direct_permission_to(synapse_test_helper):
    def _m(entity, principal, access_types=None):
        entity_id = Synapsis.id_of(entity)
        principal_id = syn.core.utils.id_of(principal)

        try:
            entity_acl = synapse_test_helper.client().restGET('/entity/{0}/acl'.format(entity_id))
        except SynapseHTTPError as ex:
            entity_acl = None
            if ex.response.status_code == 404:
                # The requested ACL does not exist. This entity inherits its permissions from: /entity/syn0000000/acl
                return False
            else:
                raise
        user_access = Utils.find(entity_acl['resourceAccess'], lambda a: str(a.get('principalId')) == str(principal_id))
        current_access_types = user_access['accessType'] if user_access else []
        if access_types is None:
            return len(current_access_types) > 0
        else:
            return set(current_access_types) == set(access_types)

    yield _m
