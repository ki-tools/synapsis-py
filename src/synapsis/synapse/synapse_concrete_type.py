from __future__ import annotations
import typing as t
import synapseclient.core.constants.concrete_types as ct
import synapseclient.core.utils as syn_utils
from ..core import utils, LazyReadOnlyAttribute


class SynapseConcreteType(object):
    code: str
    name: str

    _UNKNOWN_CODE_: t.Final[str] = 'UNKNOWN.Unknown'

    def __init__(self, code: str):
        self.code = code
        self.name = code.split('.')[-1]
        if self.name.endswith('Entity'):
            self.name = self.name.removesuffix('Entity')

    @property
    def is_project(self):
        return self.code == self.PROJECT_ENTITY.code

    @property
    def is_folder(self):
        return self.code == self.FOLDER_ENTITY.code

    @property
    def is_file(self):
        return self.code == self.FILE_ENTITY.code

    @property
    def is_unknown(self):
        return self.code == self.UNKNOWN.code

    @classmethod
    def get(cls, obj: str | t.Mapping | SynapseConcreteType) -> SynapseConcreteType:
        if isinstance(obj, str):
            code = obj
        elif isinstance(obj, SynapseConcreteType):
            code = obj.code
        else:
            code = syn_utils.concrete_type_of(obj)

        return utils.find(cls.ALL, lambda c: c.code == code, cls.UNKNOWN)

    @classmethod
    def is_a(cls, obj: str | t.Mapping | SynapseConcreteType, synapse_concrete_type: SynapseConcreteType):
        """
        Gets if 'obj' is a 'synapse_concrete_type'.

        :param obj: The object to check.
        :param synapse_concrete_type: The SynapseConcreteType to check against 'obj'.
        :return: True if 'obj' is a 'synapse_concrete_type'.
        """
        concrete_type_for_obj = cls.get(obj)
        return concrete_type_for_obj is not None and concrete_type_for_obj.code == synapse_concrete_type.code

    def __is_generic__(self, item: str) -> bool:
        item = item.replace('is_', '').upper()
        for sct in self.ALL:
            if sct.name.upper() == item or sct.code.upper().endswith('.{0}'.format(item)):
                return self.code == sct.code
        raise AttributeError('{0} does not have concrete_type matching: {1}'.format(self, item))

    def __getattr__(self, item):
        if item.lower().startswith('is_'):
            return self.__is_generic__(item)
        else:
            return object.__getattribute__(self, item)

    @classmethod
    def __all__(cls) -> list[SynapseConcreteType]:
        """
        Gets all the SynapseConcreteTypes.

        :return: list of SynapseConcreteType
        """
        return [a.__get__(None, cls) for _, a in
                utils.select(LazyReadOnlyAttribute.find(cls), lambda a: a[-1].context is not False)]

    @classmethod
    def __lazy_factory__(cls, concrete_type: str) -> SynapseConcreteType:
        """
        Creates a new SynapseConcreteType for a SynapseConcreteType.code.
        :param concrete_type: The concrete_type to create a SynapseConcreteType for.
        :return: SynapseConcreteType
        """
        if concrete_type == 'UNKNOWN':
            return cls(cls._UNKNOWN_CODE_)
        else:
            return cls(getattr(ct, concrete_type))

    ALL: t.ClassVar[list[SynapseConcreteType]] = \
        LazyReadOnlyAttribute(__all__, _context=False, _singleton=True)

    UNKNOWN: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    SYNAPSE_S3_STORAGE_LOCATION_SETTING: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    EXTERNAL_S3_STORAGE_LOCATION_SETTING: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    SYNAPSE_S3_UPLOAD_DESTINATION: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    EXTERNAL_UPLOAD_DESTINATION: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    EXTERNAL_S3_UPLOAD_DESTINATION: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    EXTERNAL_OBJECT_STORE_UPLOAD_DESTINATION: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    EXTERNAL_OBJECT_STORE_FILE_HANDLE: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    EXTERNAL_FILE_HANDLE: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    S3_FILE_HANDLE: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    ROW_REFERENCE_SET_RESULTS: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    ENTITY_UPDATE_RESULTS: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    TABLE_SCHEMA_CHANGE_RESPONSE: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    UPLOAD_TO_TABLE_RESULT: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    PARTIAL_ROW_SET: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    APPENDABLE_ROWSET_REQUEST: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    COLUMN_MODEL: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    FILE_ENTITY: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    FOLDER_ENTITY: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    LINK_ENTITY: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    PROJECT_ENTITY: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    TABLE_ENTITY: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    MULTIPART_UPLOAD_REQUEST: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)

    MULTIPART_UPLOAD_COPY_REQUEST: t.ClassVar[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, LazyReadOnlyAttribute.ATTR_NAME_ARG, _singleton=True)
