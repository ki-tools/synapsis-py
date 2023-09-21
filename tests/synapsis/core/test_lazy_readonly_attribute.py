import pytest
from synapsis import Synapsis
from synapsis.core import LazyReadOnlyAttribute


def test_it_works():
    ct = Synapsis.ConcreteTypes.PROJECT_ENTITY
    assert ct.is_project
    assert ct.is_folder is False
    assert ct.is_file is False
    # TODO: add more tests.
