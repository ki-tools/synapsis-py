import pytest
import os
import synapseclient
from synapsis import Synapsis
import synapseclient as syn


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


def test_is_synapse_id(syn_project):
    for id in [None, '', ' ', 'syn', 'synA', 'ssyn123', 'syn123z']:
        assert Synapsis.Utils.is_synapse_id(id) is False
        assert Synapsis.Utils.is_synapse_id(id, exists=True) is False

    for id in ['syn9999999999', 'SyN9999999999', ' sYn9999999999 ']:
        assert Synapsis.Utils.is_synapse_id(id) is True
        assert Synapsis.Utils.is_synapse_id(id, exists=True) is False

    assert Synapsis.Utils.is_synapse_id(syn_project.id) is True
    assert Synapsis.Utils.is_synapse_id(syn_project.id, exists=True) is True


def test_id_of():
    assert Synapsis.Utils.id_of('syn123') == 'syn123'
    assert Synapsis.Utils.id_of(synapseclient.Project(id='syn123')) == 'syn123'


async def test_md5sum(synapse_test_helper):
    file = synapse_test_helper.create_temp_file(content='1234567890')
    items = [
        Synapsis.Utils.md5sum(file),
        await Synapsis.Chain.Utils.md5sum(file)
    ]
    assert_match(items, is_a=str, equals='e807f1fcf82d132f9bb018ca6738a19f')

    items = [
        Synapsis.Utils.md5sum(file, as_bytes=True),
        await Synapsis.Chain.Utils.md5sum(file, as_bytes=True)
    ]
    assert_match(items, is_a=bytes, equals=b'\xe8\x07\xf1\xfc\xf8-\x13/\x9b\xb0\x18\xcag8\xa1\x9f')


def test_sanitize_entity_name(synapse_test_helper):
    name = Synapsis.Utils.sanitize_entity_name('abc.)(%&^%$^(*&.txt')
    assert name == 'abc.)(______(__.txt'
    name = Synapsis.Utils.sanitize_entity_name('abc.)(%&^%$^(*&.txt', replace_char='|')
    assert name == 'abc.)(||||||(||.txt'
    name = Synapsis.Utils.sanitize_entity_name('abc.)(%&^%$^(*&.txt', replace_char='')
    assert name == 'abc.)((.txt'


async def test_find_entity(synapse_test_helper, syn_project, syn_folder, syn_file):
    for entity in [syn_project, syn_folder, syn_file]:
        items = [
            Synapsis.Utils.find_entity(entity.name, parent=entity.parentId),
            await Synapsis.Chain.Utils.find_entity(entity.name, parent=entity.parentId)
        ]
        assert_match(items, equals=entity)

    assert Synapsis.Utils.find_entity(synapse_test_helper.uniq_name(), parent=syn_project) is None

    file = Synapsis.Utils.find_entity(syn_file.name, parent=syn_file.parentId)
    assert file is not None
    assert len(file.files) > 0

    file = Synapsis.Utils.find_entity(syn_file.name, parent=syn_file.parentId, downloadFile=False)
    assert file is not None
    assert len(file.files) == 0


async def test_delete_skip_trash(synapse_test_helper):
    project = synapse_test_helper.create_project()
    Synapsis.Utils.delete_skip_trash(project)
    with pytest.raises(syn.core.exceptions.SynapseHTTPError) as e:
        synapse_test_helper.client().get(project.id)
    assert e.value.response.status_code == 404
    # Can get one of two responses. The entity will still hit the trash can but be purged soon.
    assert 'is in trash can' in e.value.response.text or 'does not exist' in e.value.response.text


async def test_set_entity_permission(synapse_test_helper, syn_project, other_test_user, has_permission_to):
    team = synapse_test_helper.create_team()

    # Add team permission.
    assert has_permission_to(syn_project, team, Synapsis.Permissions.CAN_VIEW.access_types) is False
    assert Synapsis.Utils.set_entity_permission(syn_project, team, permission=Synapsis.Permissions.CAN_VIEW)
    assert Synapsis.Utils.set_entity_permission(syn_project, team, permission=Synapsis.Permissions.CAN_VIEW) is None
    assert has_permission_to(syn_project, team, Synapsis.Permissions.CAN_VIEW.access_types)

    # Remove team permission.
    Synapsis.Utils.set_entity_permission(syn_project, team, permission=None)
    assert has_permission_to(syn_project, team) is False

    # Add user permission.
    assert has_permission_to(syn_project, other_test_user, Synapsis.Permissions.CAN_VIEW.access_types) is False
    assert await Synapsis.Chain.Utils.set_entity_permission(syn_project, other_test_user,
                                                            permission=Synapsis.Permissions.CAN_VIEW.code)
    assert await Synapsis.Chain.Utils.set_entity_permission(syn_project, other_test_user,
                                                            permission=Synapsis.Permissions.CAN_VIEW.code) is None
    assert has_permission_to(syn_project, other_test_user, Synapsis.Permissions.CAN_VIEW.access_types)

    # Remove user permission.
    assert await Synapsis.Chain.Utils.set_entity_permission(syn_project, other_test_user,
                                                            permission=Synapsis.Permissions.NO_PERMISSION)
    assert await Synapsis.Chain.Utils.set_entity_permission(syn_project, other_test_user, permission=None) is None
    assert has_permission_to(syn_project, other_test_user) is False


async def test_get_bundle(synapse_test_helper, syn_project):
    bundle = Synapsis.Utils.get_bundle(
        syn_project,
        include_entity=True,
        include_annotations=True,
        include_permissions=True,
        include_entity_path=True,
        include_has_children=True,
        include_access_control_list=True,
        include_file_handles=True,
        include_table_bundle=True,
        include_root_wiki_id=True,
        include_benefactor_acl=True,
        include_doi_association=True,
        include_file_name=True,
        include_thread_count=True,
        include_restriction_information=True
    )
    assert bundle['entity']['id'] == syn_project.id


async def test_copy_file_handles_batch(synapse_test_helper, syn_project, syn_file):
    from_file_handle = syn_file['_file_handle']
    copied_file_handles = Synapsis.Utils.copy_file_handles_batch([from_file_handle['id']],
                                                                 ["FileEntity"],
                                                                 [syn_file.id])
    copy_result = copied_file_handles[0]
    new_data_file_handle_id = copy_result['newFileHandle']['id']
    file_copy = Synapsis.Synapse.store(syn.File(
        name=syn_file.name,
        dataFileHandleId=new_data_file_handle_id,
        parentId=Synapsis.id_of(syn_project)))
    assert file_copy
    synapse_test_helper.dispose_of(file_copy)
    file_copy_handle = file_copy['_file_handle']
    assert file_copy_handle['id'] != from_file_handle['id']
    assert file_copy_handle['contentMd5'] == from_file_handle['contentMd5']


async def test_get_synapse_path(synapse_test_helper, syn_project, syn_folder, syn_file):
    expected_path = syn_project.name
    path = Synapsis.Utils.get_synapse_path(syn_project)
    assert path == expected_path

    expected_path = '{0}/{1}'.format(syn_project.name, syn_folder.name)
    path = Synapsis.Utils.get_synapse_path(syn_folder)
    assert path == expected_path

    expected_path = '{0}/{1}/{2}'.format(syn_project.name, syn_folder.name, syn_file.name)
    path = Synapsis.Utils.get_synapse_path(syn_file)
    assert path == expected_path


async def test_get_filehandle(synapse_test_helper, syn_file):
    from_file_handle = syn_file['_file_handle']
    file_handle = Synapsis.Utils.get_filehandle(syn_file)
    assert file_handle['id'] == from_file_handle['id']


async def test_get_filehandles(synapse_test_helper, syn_file):
    from_file_handle = syn_file['_file_handle']

    file_handles = Synapsis.Utils.get_filehandles([(syn_file.id, from_file_handle['id'])])
    assert len(file_handles) == 1
    assert file_handles[0]['fileHandleId'] == from_file_handle['id']

    file_handles = Synapsis.Utils.get_filehandles([(syn_file, from_file_handle)])
    assert len(file_handles) == 1
    assert file_handles[0]['fileHandleId'] == from_file_handle['id']


async def test_get_project(synapse_test_helper, syn_project, syn_folder, syn_file):
    for entity in [syn_project, syn_folder, syn_file]:
        items = [
            Synapsis.Utils.get_project(entity),
            await Synapsis.Chain.Utils.get_project(entity)
        ]
        assert_match(items, is_a=syn.Project, equals=lambda items: all_items_match(items, attr='id'))


async def test_invite_to_team(synapse_test_helper, other_test_user, is_invited_to_team, is_manager_on_team):
    team = synapse_test_helper.create_team()
    test_email = os.environ.get('TEST_EMAIL')

    assert is_invited_to_team(team, test_email) is False
    res = await Synapsis.Chain.Utils.invite_to_team(team, test_email)
    assert res
    assert is_invited_to_team(team, test_email)

    with pytest.raises(Exception) as ex:
        Synapsis.Utils.invite_to_team(team, test_email, as_manager=True)
    assert 'Cannot invite emails as managers' in str(ex)

    assert is_invited_to_team(team, other_test_user) is False
    res = Synapsis.Utils.invite_to_team(team, other_test_user)
    assert res
    assert is_invited_to_team(team, other_test_user)
    assert is_manager_on_team(team, other_test_user) is False

    team_res, manager_res = await Synapsis.Chain.Utils.invite_to_team(team, other_test_user, as_manager=True)
    assert team_res is None
    assert manager_res
    assert is_manager_on_team(team, other_test_user)


async def test_set_team_permission(synapse_test_helper, other_test_user_credentials, other_test_user,
                                   is_invited_to_team,
                                   is_manager_on_team, accept_team_invite):
    other_username, other_password = other_test_user_credentials

    team = synapse_test_helper.create_team()
    Synapsis.Utils.invite_to_team(team, other_test_user)
    assert is_invited_to_team(team, other_test_user)
    accept_team_invite(team, other_test_user, email=other_username, password=other_password)
    assert is_invited_to_team(team, other_test_user) is False

    assert is_manager_on_team(team, other_test_user) is False
    assert await Synapsis.Chain.Utils.set_team_permission(team, other_test_user, None)
    assert is_manager_on_team(team, other_test_user) is False

    assert await Synapsis.Chain.Utils.set_team_permission(team, other_test_user, Synapsis.Permissions.TEAM_MANAGER)
    assert is_manager_on_team(team, other_test_user)
    assert await Synapsis.Chain.Utils.set_team_permission(team, other_test_user,
                                                          Synapsis.Permissions.TEAM_MANAGER) is None
    assert is_manager_on_team(team, other_test_user)
    assert Synapsis.Utils.set_team_permission(team, other_test_user, Synapsis.Permissions.NO_PERMISSION)
    assert is_manager_on_team(team, other_test_user) is False


async def test_find_data_file_handle(synapse_test_helper, syn_file):
    expected_file_handle_id = syn_file['dataFileHandleId']
    bundle = Synapsis.Utils.get_bundle(syn_file, include_file_handles=True)
    bundle_filehandles = bundle['fileHandles']
    for source in [syn_file, bundle, bundle_filehandles]:
        assert Synapsis.Utils.find_data_file_handle(source)['id'] == expected_file_handle_id
        assert Synapsis.Utils.find_data_file_handle(source, data_file_handle_id=expected_file_handle_id)[
                   'id'] == expected_file_handle_id