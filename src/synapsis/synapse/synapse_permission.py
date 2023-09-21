from __future__ import annotations
import typing as t
from enum import Flag, auto
from ..core import utils, exceptions, LazyReadOnlyAttribute

AccessTypes = t.NewType('AccessTypes', list[str])
PermissionCode = t.NewType('PermissionCode', str)


class Contexts(Flag):
    NO_PERMISSION = auto()
    ENTITY = auto()
    TEAM = auto()
    PERMISSIONS = NO_PERMISSION | ENTITY | TEAM

    ATTR_ALL_PERMISSIONS = auto()
    ATTR_ENTITY_PERMISSIONS = auto()
    ATTR_TEAM_PERMISSIONS = auto()
    ATTRIBUTES = ATTR_ALL_PERMISSIONS | ATTR_ENTITY_PERMISSIONS | ATTR_TEAM_PERMISSIONS


class SynapsePermission(object):
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
        found = utils.find(cls.ALL,
                           lambda p: p.code == (code if code else p.code) and
                                     set(p.access_types) == set(access_types if access_types else p.access_types))
        if raises and found is None:
            raise exceptions.NotFoundError(
                'Could not find SynapsePermission with code: {0}, access_types: {1}.'.format(code, access_types))
        return found

    @classmethod
    def __all__(cls, context: t.Optional[Contexts] = Contexts.PERMISSIONS) -> list[SynapsePermission]:
        """
        Gets all the SynapsePermissions.

        :return: list of SynapsePermission
        """
        return [a.__get__(None, cls) for _, a in
                utils.select(LazyReadOnlyAttribute.find(cls),
                             lambda a: a[-1].context & context if context else not a[-1].context & Contexts.ATTRIBUTES)]

    ALL: t.ClassVar[list[SynapsePermission]] = \
        LazyReadOnlyAttribute(__all__, context=Contexts.PERMISSIONS, _context=Contexts.ATTR_ALL_PERMISSIONS,
                              _singleton=True)

    ENTITY_PERMISSIONS: t.Final[list[SynapsePermission]] = \
        LazyReadOnlyAttribute(__all__, context=Contexts.ENTITY, _context=Contexts.ATTR_ENTITY_PERMISSIONS,
                              _singleton=True)

    TEAM_PERMISSIONS: t.Final[list[SynapsePermission]] = \
        LazyReadOnlyAttribute(__all__, context=Contexts.TEAM, _context=Contexts.ATTR_TEAM_PERMISSIONS, _singleton=True)

    NO_PERMISSION: t.Final[SynapsePermission] = \
        LazyReadOnlyAttribute(lambda: SynapsePermission('NO_PERMISSION',
                                                        'No Permission', []),
                              _context=Contexts.NO_PERMISSION | Contexts.ENTITY | Contexts.TEAM, _singleton=True)

    ADMIN: t.Final[SynapsePermission] = \
        LazyReadOnlyAttribute(lambda: SynapsePermission('ADMIN',
                                                        'Administrator',
                                                        ['UPDATE',
                                                         'DELETE',
                                                         'CHANGE_PERMISSIONS',
                                                         'CHANGE_SETTINGS',
                                                         'CREATE',
                                                         'DOWNLOAD',
                                                         'READ',
                                                         'MODERATE']), _context=Contexts.ENTITY, _singleton=True)

    CAN_EDIT_AND_DELETE: t.Final[SynapsePermission] = \
        LazyReadOnlyAttribute(lambda: SynapsePermission('CAN_EDIT_AND_DELETE',
                                                        'Can Edit and Delete',
                                                        ['DOWNLOAD',
                                                         'UPDATE',
                                                         'CREATE',
                                                         'DELETE',
                                                         'READ']), _context=Contexts.ENTITY, _singleton=True)

    CAN_EDIT: t.Final[SynapsePermission] = \
        LazyReadOnlyAttribute(lambda: SynapsePermission('CAN_EDIT',
                                                        'Can Edit',
                                                        ['DOWNLOAD',
                                                         'UPDATE',
                                                         'CREATE',
                                                         'READ']), _context=Contexts.ENTITY, _singleton=True)

    CAN_DOWNLOAD: t.Final[SynapsePermission] = \
        LazyReadOnlyAttribute(lambda: SynapsePermission('CAN_DOWNLOAD',
                                                        'Can Download',
                                                        ['DOWNLOAD',
                                                         'READ']), _context=Contexts.ENTITY, _singleton=True)

    CAN_VIEW: t.Final[SynapsePermission] = \
        LazyReadOnlyAttribute(lambda: SynapsePermission('CAN_VIEW',
                                                        'Can View',
                                                        ['READ']), _context=Contexts.ENTITY, _singleton=True)

    TEAM_MANAGER: t.Final[SynapsePermission] = \
        LazyReadOnlyAttribute(lambda: SynapsePermission('TEAM_MANAGER',
                                                        'Team Manager',
                                                        ['SEND_MESSAGE',
                                                         'READ',
                                                         'UPDATE',
                                                         'TEAM_MEMBERSHIP_UPDATE',
                                                         'DELETE']), _context=Contexts.TEAM, _singleton=True)
