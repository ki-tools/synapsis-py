import pytest
from synapsis.synapse import SynapsePermission
from synapsis.core.exceptions import NotFoundError
from synapsis.core import Utils
from synapsis.synapse.synapse_permission import SynapsePermissions

entity_permission_codes = [
    'NO_PERMISSION',
    'ADMIN',
    'CAN_EDIT_AND_DELETE',
    'CAN_EDIT',
    'CAN_DOWNLOAD',
    'CAN_VIEW'
]

team_permission_codes = [
    'NO_PERMISSION',
    'TEAM_MANAGER'
]

all_permission_codes = set(entity_permission_codes + team_permission_codes)


def test_contexts():
    entity_permissions = SynapsePermission.ENTITY_PERMISSIONS
    assert len(entity_permissions) == len(entity_permission_codes)
    for code in entity_permission_codes:
        p = Utils.find(entity_permissions, lambda ep: ep.code == code, None)
        assert p is not None
        assert p.code == code

    team_permissions = SynapsePermission.TEAM_PERMISSIONS
    assert len(team_permissions) == len(team_permission_codes)
    for code in team_permission_codes:
        p = Utils.find(team_permissions, lambda ep: ep.code == code, None)
        assert p is not None
        assert p.code == code

    all_permissions = SynapsePermission.ALL
    assert len(all_permissions) == len(all_permission_codes)
    for code in all_permission_codes:
        p = Utils.find(all_permissions, lambda ep: ep.code == code, None)
        assert p is not None
        assert p.code == code


def test_cached_attributes():
    for code in all_permission_codes:
        perm1 = getattr(SynapsePermission, code)
        perm2 = getattr(SynapsePermission, code)
        assert perm1.code == perm2.code == code
        assert perm1 == perm2


def test_find_by():
    for perm in SynapsePermission.ALL:
        assert SynapsePermission.find_by(code=perm.code) == perm
        assert SynapsePermission.find_by(code=perm.code.lower()) == perm

        assert SynapsePermission.find_by(access_types=perm.access_types) == perm
        assert SynapsePermission.find_by(access_types=[a.lower() for a in perm.access_types]) == perm

        assert SynapsePermission.find_by(code=perm.code, access_types=perm.access_types) == perm
        assert SynapsePermission.find_by(code='NOPE', access_types=perm.access_types) is None
        assert SynapsePermission.find_by(code=perm.code, access_types=['NOPE']) is None

        with pytest.raises(ValueError) as ex:
            SynapsePermission.find_by()
        assert 'code or access_types are required.' in str(ex)

        assert SynapsePermission.find_by(code='NOPE', raises=False) is None

        with pytest.raises(NotFoundError) as ex:
            SynapsePermission.find_by(code='NOPE', raises=True)
        assert 'Could not find SynapsePermission' in str(ex)


def test_are_equal():
    invalid = SynapsePermission(code='INVALID', name='INVALID', access_types=['INVALID'])
    for perm in SynapsePermission.ALL:
        same = SynapsePermission(code=perm.code, name=perm.name, access_types=perm.access_types)
        assert perm != same
        assert perm.access_types == same.access_types
        assert perm.equals(same)

        # True
        for args in [
            (perm, same),
            (perm.access_types, same),
            (perm, same.access_types),
            (perm.access_types, same.access_types)
        ]:
            assert SynapsePermission.are_equal(*args)
            assert SynapsePermission.are_equal(*args)

        # False
        for arg in [invalid, None]:
            assert perm.equals(arg) is False

        for args in [
            (None, same.access_types),
            (perm.access_types, None),
            (None, None),
            (perm, invalid)
        ]:
            assert SynapsePermission.are_equal(*args) is False
            assert SynapsePermission.are_equal(*args) is False
