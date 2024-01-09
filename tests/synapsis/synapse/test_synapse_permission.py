import pytest
from synapsis.synapse import SynapsePermission
from synapsis.core.exceptions import NotFoundError
from synapsis.core import Utils, none
import itertools

entity_permission_codes = Utils.map(SynapsePermission.ENTITY_PERMISSIONS, key='code')
team_permission_codes = Utils.map(SynapsePermission.TEAM_PERMISSIONS, key='code')
all_permission_codes = set(entity_permission_codes + team_permission_codes)


def test_permission_sets():
    entity_permissions = SynapsePermission.ENTITY_PERMISSIONS
    assert len(entity_permissions) == len(entity_permission_codes)
    for code in entity_permission_codes:
        p = Utils.find(entity_permissions, lambda ep: ep.code == code)
        assert p is not None
        assert p.code == code

    team_permissions = SynapsePermission.TEAM_PERMISSIONS
    assert len(team_permissions) == len(team_permission_codes)
    for code in team_permission_codes:
        p = Utils.find(team_permissions, lambda ep: ep.code == code)
        assert p is not None
        assert p.code == code

    all_permissions = SynapsePermission.ALL
    assert len(all_permissions) == len(all_permission_codes)
    for code in all_permission_codes:
        p = Utils.find(all_permissions, lambda ep: ep.code == code)
        assert p is not None
        assert p.code == code


def test_cached_attributes():
    for code in all_permission_codes:
        perm1 = getattr(SynapsePermission, code)
        perm2 = getattr(SynapsePermission, code)
        assert perm1.code == perm2.code == code
        assert perm1 == perm2


def test_get():
    invalid = SynapsePermission(code='INVALID', name='INVALID', access_types=['INVALID'])
    for perm in SynapsePermission.ALL:
        for arg in [perm, perm.code.upper(), perm.code.lower(), perm.access_types] + \
                   [list([a.lower() for a in perm.access_types])] + \
                   [list([a.upper() for a in perm.access_types])]:
            assert SynapsePermission.get(arg) == perm

    for arg, default, expected in [
        (None, None, None),
        (None, SynapsePermission.NO_PERMISSION, SynapsePermission.NO_PERMISSION),
        (None, SynapsePermission.ADMIN, SynapsePermission.ADMIN),
        (invalid, SynapsePermission.NO_PERMISSION, SynapsePermission.NO_PERMISSION),
        (invalid, None, None),
        (invalid.code, None, None),
        (invalid.access_types, None, None),
        (invalid, none, NotFoundError)
    ]:
        if expected == NotFoundError:
            with pytest.raises(expected):
                SynapsePermission.get(arg, default)
        else:
            assert SynapsePermission.get(arg, default) == expected


def test_equals():
    invalid = SynapsePermission(code='INVALID', name='INVALID', access_types=['INVALID'])
    assert SynapsePermission.get(invalid, None) is None
    assert SynapsePermission.are_equal(None, None) is False

    for perm in SynapsePermission.ALL:
        same = SynapsePermission(code=perm.code, name=perm.name, access_types=perm.access_types)
        other = Utils.first(SynapsePermission.ALL, lambda p: p.code != perm.code)
        assert id(same) != id(perm)
        assert perm == same
        assert same.code == perm.code
        assert same.access_types == perm.access_types
        assert perm.equals(same)
        assert same.equals(perm)
        assert other.code != perm.code
        assert other.access_types != perm.access_types
        assert SynapsePermission.are_equal(perm, other) is False

        if perm.code == SynapsePermission.NO_PERMISSION.code:
            assert perm.none is True
        else:
            assert perm.none is False

        # True
        permutations = list(itertools.permutations(
            [perm, perm.code, perm.access_types, same, same.code, same.access_types], r=2))
        for a, b in permutations:
            assert SynapsePermission.are_equal(a, b)
            if isinstance(a, SynapsePermission) and isinstance(b, SynapsePermission):
                assert a == b
            elif isinstance(a, SynapsePermission) or isinstance(b, SynapsePermission):
                assert a != b
            if isinstance(a, SynapsePermission):
                assert a.equals(b)
            if isinstance(b, SynapsePermission):
                assert b.equals(a)

        # False
        products = list(itertools.product(
            [perm, perm.code, perm.access_types, invalid, invalid.code, invalid.access_types],
            [other, other.code, other.access_types, '', ' ', 'NOPE']
        ))
        for a, b in products:
            a_perm = SynapsePermission.get(a, None)
            b_perm = SynapsePermission.get(b, None)
            expected = a_perm == SynapsePermission.NO_PERMISSION and b_perm == SynapsePermission.NO_PERMISSION

            assert SynapsePermission.are_equal(a, b) is expected
            if isinstance(a, SynapsePermission):
                assert a.equals(b) is expected
                if expected:
                    assert a == b
                else:
                    assert a != b
            if isinstance(b, SynapsePermission):
                assert b.equals(a) is expected
                if expected:
                    assert b == a
                else:
                    assert b != a


def test___lt__():
    last_perm = None
    for perm in SynapsePermission.ENTITY_PERMISSIONS:
        if last_perm:
            assert perm > last_perm
            assert last_perm < perm
            assert perm != last_perm
        last_perm = perm

    with pytest.raises(ValueError) as ex:
        SynapsePermission.ADMIN > SynapsePermission.TEAM_MANAGER
    assert 'Self and other must belong to the same permission set.' in str(ex)
