import pytest
import os
import tempfile
from synapsis.synapse.synapse import Synapse
import synapseclient


def test_it_fixes_cache_root_dir(mocker):
    expected_path = os.path.expandvars(os.path.expanduser((synapseclient.core.cache.CACHE_ROOT_DIR)))
    assert os.access(expected_path, os.W_OK) is True
    synapse = Synapse()
    assert synapse.cache.cache_root_dir == expected_path

    mocker.patch('os.access', return_value=False)
    assert os.access(expected_path, os.W_OK) is False
    synapse = Synapse()
    assert synapse.cache.cache_root_dir != expected_path
    assert os.path.dirname(synapse.cache.cache_root_dir) == tempfile.gettempdir()
