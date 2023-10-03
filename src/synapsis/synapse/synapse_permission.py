from __future__ import annotations
import typing as t
from collections.abc import Collection
import functools
from ..core import Utils, exceptions, Narg, none

AccessTypes = t.NewType('AccessTypes', list[str])
PermissionCode = t.NewType('PermissionCode', str)


class SynapsePermissions(type):
    @property
    @functools.cache
    def ALL(cls) -> list[SynapsePermission]:
        return Utils.unique(cls.ENTITY_PERMISSIONS + cls.TEAM_PERMISSIONS, key='code')

    @property
    @functools.cache
    def ENTITY_PERMISSIONS(cls) -> list[SynapsePermission]:
        return [
            cls.NO_PERMISSION,
            cls.ADMIN,
            cls.CAN_EDIT_AND_DELETE,
            cls.CAN_EDIT,
            cls.CAN_DOWNLOAD,
            cls.CAN_VIEW
        ]

    @property
    @functools.cache
    def TEAM_PERMISSIONS(cls) -> list[SynapsePermission]:
        return [
            cls.NO_PERMISSION,
            cls.TEAM_MANAGER
        ]

    @property
    @functools.cache
    def NO_PERMISSION(cls) -> SynapsePermission:
        return SynapsePermission('NO_PERMISSION', 'No Permission', [])

    @property
    @functools.cache
    def ADMIN(cls) -> SynapsePermission:
        return SynapsePermission('ADMIN',
                                 'Administrator',
                                 ['UPDATE',
                                  'DELETE',
                                  'CHANGE_PERMISSIONS',
                                  'CHANGE_SETTINGS',
                                  'CREATE',
                                  'DOWNLOAD',
                                  'READ',
                                  'MODERATE'])

    @property
    @functools.cache
    def CAN_EDIT_AND_DELETE(cls) -> SynapsePermission:
        return SynapsePermission('CAN_EDIT_AND_DELETE',
                                 'Can Edit and Delete',
                                 ['DOWNLOAD',
                                  'UPDATE',
                                  'CREATE',
                                  'DELETE',
                                  'READ'])

    @property
    @functools.cache
    def CAN_EDIT(cls) -> SynapsePermission:
        return SynapsePermission('CAN_EDIT',
                                 'Can Edit',
                                 ['DOWNLOAD',
                                  'UPDATE',
                                  'CREATE',
                                  'READ'])

    @property
    @functools.cache
    def CAN_DOWNLOAD(cls) -> SynapsePermission:
        return SynapsePermission('CAN_DOWNLOAD',
                                 'Can Download',
                                 ['DOWNLOAD',
                                  'READ'])

    @property
    @functools.cache
    def CAN_VIEW(cls) -> SynapsePermission:
        return SynapsePermission('CAN_VIEW',
                                 'Can View',
                                 ['READ'])

    @property
    @functools.cache
    def TEAM_MANAGER(cls) -> SynapsePermission:
        return SynapsePermission('TEAM_MANAGER',
                                 'Team Manager',
                                 ['SEND_MESSAGE',
                                  'READ',
                                  'UPDATE',
                                  'TEAM_MEMBERSHIP_UPDATE',
                                  'DELETE'])


class SynapsePermission(object, metaclass=SynapsePermissions):

    def __init__(self, code: PermissionCode, name: str, access_types: AccessTypes) -> None:
        self._code = code
        self._name = name
        self._access_types = sorted(access_types)

    @property
    def code(self) -> PermissionCode:
        return self._code

    @property
    def name(self) -> str:
        return self._name

    @property
    def access_types(self) -> AccessTypes:
        return self._access_types

    def equals(self, other: SynapsePermission | AccessTypes | PermissionCode) -> bool:
        """Gets if self and other are the same permission."""
        return self.are_equal(self, other)

    @classmethod
    def are_equal(cls,
                  a: SynapsePermission | AccessTypes | PermissionCode,
                  b: SynapsePermission | AccessTypes | PermissionCode) -> bool:
        """Gets if two permissions are the same."""
        if a is None or b is None:
            return False
        a_perm = cls.get(a, None)
        b_perm = cls.get(b, None)
        if not (a_perm and b_perm):
            return False
        else:
            return a_perm.code == b_perm.code and a_perm.access_types == b_perm.access_types

    @classmethod
    def get(cls,
            value: SynapsePermission | PermissionCode | AccessTypes | None,
            default: SynapsePermission | None = none) -> SynapsePermission:
        """Gets a SynapsePermission"""
        permission = None
        if isinstance(value, SynapsePermission):
            permission = Utils.find(cls.ALL, lambda p: p.code == value.code and p.access_types == value.access_types)
        elif isinstance(value, str):
            _value = value.upper()
            permission = Utils.find(cls.ALL, key='code', value=_value)
        elif isinstance(value, Collection):
            _value = sorted(Utils.map(value, str.upper))
            permission = Utils.find(cls.ALL, key='access_types', value=_value)
        elif value is not None:
            raise ValueError('Invalid value: {0}'.find(value))

        if permission is None:
            if Narg.is_narg(default):
                raise exceptions.NotFoundError('Could not find SynapsePermission with: {0}'.format(value))
            else:
                return default
        else:
            return permission
