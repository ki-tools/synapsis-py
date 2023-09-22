from __future__ import annotations
import typing as t
import functools
import synapseclient.core.constants.concrete_types as ct
import synapseclient.core.utils as syn_utils
from ..core import Utils


class SynapseConcreteTypes(type):
    _UNKNOWN_CODE_: t.Final[str] = 'UNKNOWN.Unknown'

    @property
    @functools.cache
    def ALL(cls) -> list[SynapseConcreteType]:
        return [
            cls.UNKNOWN,
            cls.SYNAPSE_S3_STORAGE_LOCATION_SETTING,
            cls.EXTERNAL_S3_STORAGE_LOCATION_SETTING,
            cls.SYNAPSE_S3_UPLOAD_DESTINATION,
            cls.EXTERNAL_UPLOAD_DESTINATION,
            cls.EXTERNAL_S3_UPLOAD_DESTINATION,
            cls.EXTERNAL_OBJECT_STORE_UPLOAD_DESTINATION,
            cls.EXTERNAL_OBJECT_STORE_FILE_HANDLE,
            cls.EXTERNAL_FILE_HANDLE,
            cls.S3_FILE_HANDLE,
            cls.ROW_REFERENCE_SET_RESULTS,
            cls.ENTITY_UPDATE_RESULTS,
            cls.TABLE_SCHEMA_CHANGE_RESPONSE,
            cls.UPLOAD_TO_TABLE_RESULT,
            cls.PARTIAL_ROW_SET,
            cls.APPENDABLE_ROWSET_REQUEST,
            cls.COLUMN_MODEL,
            cls.FILE_ENTITY,
            cls.FOLDER_ENTITY,
            cls.LINK_ENTITY,
            cls.PROJECT_ENTITY,
            cls.TABLE_ENTITY,
            cls.MULTIPART_UPLOAD_REQUEST,
            cls.MULTIPART_UPLOAD_COPY_REQUEST
        ]

    @property
    @functools.cache
    def UNKNOWN(cls) -> SynapseConcreteType:
        return SynapseConcreteType(cls._UNKNOWN_CODE_)

    @property
    @functools.cache
    def SYNAPSE_S3_STORAGE_LOCATION_SETTING(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.SYNAPSE_S3_STORAGE_LOCATION_SETTING)

    @property
    @functools.cache
    def EXTERNAL_S3_STORAGE_LOCATION_SETTING(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.EXTERNAL_S3_STORAGE_LOCATION_SETTING)

    @property
    @functools.cache
    def SYNAPSE_S3_UPLOAD_DESTINATION(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.SYNAPSE_S3_UPLOAD_DESTINATION)

    @property
    @functools.cache
    def EXTERNAL_UPLOAD_DESTINATION(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.EXTERNAL_UPLOAD_DESTINATION)

    @property
    @functools.cache
    def EXTERNAL_S3_UPLOAD_DESTINATION(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.EXTERNAL_S3_UPLOAD_DESTINATION)

    @property
    @functools.cache
    def EXTERNAL_OBJECT_STORE_UPLOAD_DESTINATION(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.EXTERNAL_OBJECT_STORE_UPLOAD_DESTINATION)

    @property
    @functools.cache
    def EXTERNAL_OBJECT_STORE_FILE_HANDLE(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.EXTERNAL_OBJECT_STORE_FILE_HANDLE)

    @property
    @functools.cache
    def EXTERNAL_FILE_HANDLE(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.EXTERNAL_FILE_HANDLE)

    @property
    @functools.cache
    def S3_FILE_HANDLE(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.S3_FILE_HANDLE)

    @property
    @functools.cache
    def ROW_REFERENCE_SET_RESULTS(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.ROW_REFERENCE_SET_RESULTS)

    @property
    @functools.cache
    def ENTITY_UPDATE_RESULTS(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.ENTITY_UPDATE_RESULTS)

    @property
    @functools.cache
    def TABLE_SCHEMA_CHANGE_RESPONSE(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.TABLE_SCHEMA_CHANGE_RESPONSE)

    @property
    @functools.cache
    def UPLOAD_TO_TABLE_RESULT(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.UPLOAD_TO_TABLE_RESULT)

    @property
    @functools.cache
    def PARTIAL_ROW_SET(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.PARTIAL_ROW_SET)

    @property
    @functools.cache
    def APPENDABLE_ROWSET_REQUEST(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.APPENDABLE_ROWSET_REQUEST)

    @property
    @functools.cache
    def COLUMN_MODEL(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.COLUMN_MODEL)

    @property
    @functools.cache
    def FILE_ENTITY(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.FILE_ENTITY)

    @property
    @functools.cache
    def FOLDER_ENTITY(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.FOLDER_ENTITY)

    @property
    @functools.cache
    def LINK_ENTITY(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.LINK_ENTITY)

    @property
    @functools.cache
    def PROJECT_ENTITY(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.PROJECT_ENTITY)

    @property
    @functools.cache
    def TABLE_ENTITY(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.TABLE_ENTITY)

    @property
    @functools.cache
    def MULTIPART_UPLOAD_REQUEST(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.MULTIPART_UPLOAD_REQUEST)

    @property
    @functools.cache
    def MULTIPART_UPLOAD_COPY_REQUEST(cls) -> SynapseConcreteType:
        return SynapseConcreteType(ct.MULTIPART_UPLOAD_COPY_REQUEST)


class SynapseConcreteType(object, metaclass=SynapseConcreteTypes):
    code: str
    name: str

    def __init__(self, code: str):
        self.code = code
        self.name = code.split('.')[-1]
        if self.name.endswith('Entity'):
            self.name = self.name.removesuffix('Entity')

    @property
    def is_project(self):
        return self.code == type(self).PROJECT_ENTITY.code

    @property
    def is_folder(self):
        return self.code == type(self).FOLDER_ENTITY.code

    @property
    def is_file(self):
        return self.code == type(self).FILE_ENTITY.code

    @property
    def is_unknown(self):
        return self.code == type(self).UNKNOWN.code

    @classmethod
    def get(cls, obj: str | t.Mapping | SynapseConcreteType) -> SynapseConcreteType:
        if isinstance(obj, str):
            code = obj
        elif isinstance(obj, SynapseConcreteType):
            code = obj.code
        else:
            code = syn_utils.concrete_type_of(obj)

        return Utils.find(cls.ALL, lambda c: c.code == code, cls.UNKNOWN)

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
        for sct in type(self).ALL:
            if sct.name.upper() == item or sct.code.upper().endswith('.{0}'.format(item)):
                return self.code == sct.code
        raise AttributeError('{0} does not have concrete_type matching: {1}'.format(self, item))

    def __getattr__(self, item):
        if item.lower().startswith('is_'):
            return self.__is_generic__(item)
        else:
            return object.__getattribute__(self, item)
