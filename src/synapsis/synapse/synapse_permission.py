from __future__ import annotations
import typing as t
import functools
from ..core import Utils, exceptions

AccessTypes = t.NewType('AccessTypes', list[str])
PermissionCode = t.NewType('PermissionCode', str)


class SynapsePermissions(type):
    @property
    @functools.cache
    def ALL(cls) -> list[SynapsePermission]:
        return [cls.NO_PERMISSION] + Utils.select(cls.ENTITY_PERMISSIONS + cls.TEAM_PERMISSIONS,
                                                  lambda p: p.code != cls.NO_PERMISSION.code)

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
        return [cls.NO_PERMISSION, cls.TEAM_MANAGER]

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
    code: PermissionCode
    name: str
    access_types: AccessTypes

    def __init__(self, code: PermissionCode, name: str, access_types: AccessTypes) -> None:
        self.code = code
        self.name = name
        self.access_types = access_types

    def equals(self, other: SynapsePermission | AccessTypes) -> bool:
        """Are equal if the access_types match."""
        return self.are_equal(self, other)

    @classmethod
    def are_equal(cls, a: SynapsePermission | AccessTypes, b: SynapsePermission | AccessTypes) -> bool:
        """Are equal if the access_types match."""
        a_access_types = a.access_types if isinstance(a, SynapsePermission) else a
        b_access_types = b.access_types if isinstance(b, SynapsePermission) else b
        if a_access_types is None or b_access_types is None:
            return False
        return set(a_access_types) == set(b_access_types)

    @classmethod
    def find_by(cls,
                code: PermissionCode = None,
                access_types: AccessTypes = None,
                raises: t.Optional[bool] = False) -> SynapsePermission | None:
        code = code.upper() if code is not None else None
        access_types = [a.upper() for a in access_types] if access_types is not None else None
        if code is None and access_types is None:
            raise ValueError('code or access_types are required.')
        found = Utils.find(cls.ALL,
                           lambda p: p.code == (code if code else p.code) and
                                     set(p.access_types) == set(access_types if access_types else p.access_types))
        if raises and found is None:
            raise exceptions.NotFoundError(
                'Could not find SynapsePermission with code: {0}, access_types: {1}.'.format(code, access_types))
        return found
