import pytest
from synapsis.synapse.synapse_concrete_type import SynapseConcreteType, SynapseConcreteTypes
import synapseclient
import synapseclient.core.constants.concrete_types as ct
from synapsis.core import Utils


def syn_concrete_types():
    result = [('UNKNOWN', SynapseConcreteTypes._UNKNOWN_CODE_)]
    for name, code in vars(ct).items():
        if name.startswith('_'):
            continue
        result.append((name, code))
    return result


def test_cached_attributes():
    for name, code in syn_concrete_types():
        sct1 = getattr(SynapseConcreteType, name)
        sct2 = getattr(SynapseConcreteType, name)
        assert sct1.code == sct2.code == code
        assert sct1 == sct2


def test_get():
    for name, code in syn_concrete_types():
        sct = SynapseConcreteType.get(code)
        assert sct.code == code
        assert SynapseConcreteType.get(sct).code == code

        if code != SynapseConcreteType.UNKNOWN.code:
            for data in [
                {'obj': synapseclient.Entity(concreteType=code), 'code': code},
                {'obj': {'concreteType': code}, 'code': code},
                {'obj': {'entity': {'concreteType': code}}, 'code': code}
            ]:
                obj = data['obj']
                expected_code = data['code']
                sct = SynapseConcreteType.get(obj)
                assert sct.code == expected_code

    assert SynapseConcreteType.get('not-real') == SynapseConcreteType.UNKNOWN

    # https://rest-docs.synapse.org/rest/org/sagebionetworks/repo/model/EntityType.html
    for data in [
        {'obj': synapseclient.Project(), 'code': ct.PROJECT_ENTITY},
        {'obj': synapseclient.Folder(parentId=1), 'code': ct.FOLDER_ENTITY},
        {'obj': synapseclient.File(parentId=1), 'code': ct.FILE_ENTITY},
        {'obj': {'entityType': 'project'}, 'code': ct.PROJECT_ENTITY},
        {'obj': {'entityType': 'folder'}, 'code': ct.FOLDER_ENTITY},
        {'obj': {'entityType': 'file'}, 'code': ct.FILE_ENTITY},
        {'obj': {'entityType': 'table'}, 'code': ct.TABLE_ENTITY},
        {'obj': {'entityType': 'link'}, 'code': ct.LINK_ENTITY},
        {'obj': {'entityType': 'entityview'}, 'code': SynapseConcreteTypes._UNKNOWN_CODE_},
        {'obj': {'entityType': 'dockerrepo'}, 'code': SynapseConcreteTypes._UNKNOWN_CODE_},
        {'obj': {'entityType': 'submissionview'}, 'code': SynapseConcreteTypes._UNKNOWN_CODE_},
        {'obj': {'entityType': 'dataset'}, 'code': SynapseConcreteTypes._UNKNOWN_CODE_},
        {'obj': {'entityType': 'datasetcollection'}, 'code': SynapseConcreteTypes._UNKNOWN_CODE_},
        {'obj': {'entityType': 'materializedview'}, 'code': SynapseConcreteTypes._UNKNOWN_CODE_},
        {'obj': {'entityType': 'virtualtable'}, 'code': SynapseConcreteTypes._UNKNOWN_CODE_}
    ]:
        obj = data['obj']
        expected_code = data['code']
        sct = SynapseConcreteType.get(obj)
        assert sct.code == expected_code


def test_is_concrete_type_and_is_a():
    project_type = SynapseConcreteType.PROJECT_ENTITY
    folder_type = SynapseConcreteType.FOLDER_ENTITY

    assert project_type.is_a(project_type)
    assert project_type.is_a(project_type.code)

    assert project_type.is_a(folder_type, project_type)
    assert project_type.is_a(folder_type.code, project_type.code)

    assert project_type.is_a(folder_type) is False
    assert project_type.is_a(folder_type.code) is False

    assert SynapseConcreteType.is_concrete_type(project_type, project_type)
    assert SynapseConcreteType.is_concrete_type(project_type.code, project_type.code)

    assert SynapseConcreteType.is_concrete_type(project_type, folder_type, project_type)

    assert SynapseConcreteType.is_concrete_type(SynapseConcreteType._UNKNOWN_CODE_, SynapseConcreteType.UNKNOWN)
    assert SynapseConcreteType.is_concrete_type(SynapseConcreteType.UNKNOWN, SynapseConcreteType.UNKNOWN)

    for name, code in syn_concrete_types():
        sct = SynapseConcreteType.get(code)
        other_sct = Utils.find(SynapseConcreteType.ALL, lambda a: a.code != sct.code)
        assert sct.is_a(sct)
        assert sct.is_a(sct.code)
        assert sct.is_a(other_sct, sct)
        assert sct.is_a(other_sct) is False
        assert SynapseConcreteType.is_concrete_type(sct, sct)
        assert SynapseConcreteType.is_concrete_type(sct.code, sct.code)
        assert SynapseConcreteType.is_concrete_type(other_sct.code, sct.code) is False

    for obj in [synapseclient.Project(), synapseclient.Folder(parentId=1), synapseclient.File(parentId=1)]:
        sct = SynapseConcreteType.get(obj)
        other_sct = Utils.find(SynapseConcreteType.ALL, lambda a: a.code != sct.code)
        assert sct.is_a(sct)
        assert sct.is_a(other_sct) is False
        assert SynapseConcreteType.is_concrete_type(obj, sct)
        assert SynapseConcreteType.is_concrete_type(obj, other_sct) is False


def test_ALL():
    for name, code in syn_concrete_types():
        assert Utils.find(SynapseConcreteType.ALL, lambda a: a.code == code)


def test_UNKNOWN():
    assert SynapseConcreteType.UNKNOWN
    assert SynapseConcreteType.UNKNOWN.code == 'UNKNOWN.Unknown'
    assert SynapseConcreteType.UNKNOWN.name == 'Unknown'
    assert SynapseConcreteType.UNKNOWN.is_unknown
    assert SynapseConcreteType.UNKNOWN.is_project is False
    assert SynapseConcreteType.UNKNOWN.is_folder is False
    assert SynapseConcreteType.UNKNOWN.is_file is False


def test___is_generic__():
    assert SynapseConcreteType.PROJECT_ENTITY.is_project
    assert SynapseConcreteType.FOLDER_ENTITY.is_folder
    assert SynapseConcreteType.FILE_ENTITY.is_file
    assert SynapseConcreteType.FILE_ENTITY.is_fileentity is True
    assert SynapseConcreteType.FILE_ENTITY.is_ColUMnModeL is False

    with pytest.raises(AttributeError):
        SynapseConcreteType.FILE_ENTITY.is_Nope

    for sct in SynapseConcreteType.ALL:
        other_sct = Utils.find(SynapseConcreteType.ALL, lambda a: a != sct)

        attr_name = 'is_{0}'.format(sct.code.split('.')[-1]).lower()
        assert getattr(sct, attr_name) is True
        assert getattr(other_sct, attr_name) is False

        attr_name = 'is_{0}'.format(sct.name)
        assert getattr(sct, attr_name) is True
        assert getattr(other_sct, attr_name) is False
