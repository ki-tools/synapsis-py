import pytest

from synapsis.synapse.synapse_concrete_type import SynapseConcreteType
import synapseclient
import synapseclient.core.constants.concrete_types as ct
from synapsis.core import utils


def syn_concrete_types():
    result = [('UNKNOWN', SynapseConcreteType._UNKNOWN_CODE_)]
    for name, code in vars(ct).items():
        if name.startswith('_'):
            continue
        result.append((name, code))
    return result


def test_lazy_attributes():
    for name, code in syn_concrete_types():
        sct1 = getattr(SynapseConcreteType, name)
        sct2 = getattr(SynapseConcreteType, name)
        assert sct1.code == sct2.code == code
        assert sct1 == sct2


def test___factory__():
    for name, code in syn_concrete_types():
        sct1 = SynapseConcreteType.__lazy_factory__(name)
        sct2 = SynapseConcreteType.__lazy_factory__(name)
        assert isinstance(sct1, SynapseConcreteType)
        assert isinstance(sct2, SynapseConcreteType)
        assert sct1.code == code
        assert sct2.code == code
        assert sct1 != sct2


def test_get():
    for name, code in syn_concrete_types():
        sct = SynapseConcreteType.get(code)
        assert sct.code == code
        assert SynapseConcreteType.get(sct).code == code
    for obj in [synapseclient.Project(), synapseclient.Folder(parentId=1), synapseclient.File(parentId=1)]:
        sct = SynapseConcreteType.get(obj)
        assert sct.code == obj['concreteType']
    assert SynapseConcreteType.get('not-real') == SynapseConcreteType.UNKNOWN


def test_is_a():
    assert SynapseConcreteType.is_a(SynapseConcreteType.PROJECT_ENTITY.code, SynapseConcreteType.PROJECT_ENTITY)
    assert SynapseConcreteType.is_a(SynapseConcreteType._UNKNOWN_CODE_, SynapseConcreteType.UNKNOWN)
    assert SynapseConcreteType.is_a(SynapseConcreteType.UNKNOWN, SynapseConcreteType.UNKNOWN)

    for name, code in syn_concrete_types():
        sct = SynapseConcreteType.get(code)
        assert SynapseConcreteType.is_a(sct.code, sct)
        other_sct = utils.find(SynapseConcreteType.ALL, lambda a: a.code != sct.code)
        assert SynapseConcreteType.is_a(other_sct.code, sct) is False

    for obj in [synapseclient.Project(), synapseclient.Folder(parentId=1), synapseclient.File(parentId=1)]:
        sct = SynapseConcreteType.get(obj)
        assert SynapseConcreteType.is_a(obj, sct)
        other_sct = utils.find(SynapseConcreteType.ALL, lambda a: a.code != sct.code)
        assert SynapseConcreteType.is_a(obj, other_sct) is False


def test_ALL():
    for name, code in syn_concrete_types():
        assert utils.find(SynapseConcreteType.ALL, lambda a: a.code == code, None)


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
        other_sct = utils.find(SynapseConcreteType.ALL, lambda a: a != sct)

        attr_name = 'is_{0}'.format(sct.code.split('.')[-1]).lower()
        assert getattr(sct, attr_name) is True
        assert getattr(other_sct, attr_name) is False

        attr_name = 'is_{0}'.format(sct.name)
        assert getattr(sct, attr_name) is True
        assert getattr(other_sct, attr_name) is False
