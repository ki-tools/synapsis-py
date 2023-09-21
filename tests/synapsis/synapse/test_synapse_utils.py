import pytest
from synapsis import Synapsis


async def test_it_routes_the_methods(synapse_test_helper, syn_project, syn_folder):
    for dirpath, dirname, filename in Synapsis.SynapseUtils.walk(syn_project):
        assert dirpath[1] in [syn_project.id, syn_project.name, syn_project, syn_folder.id, syn_folder.name, syn_folder]

    for dirpath, dirname, filename in Synapsis.SynapseUtils.walk(Synapsis.Synapse, syn_project):
        assert dirpath[1] in [syn_project.id, syn_project.name, syn_project, syn_folder.id, syn_folder.name, syn_folder]

    async for dirpath, dirname, filename in Synapsis.Chain.SynapseUtils.walk(syn_project):
        assert dirpath[1] in [syn_project.id, syn_project.name, syn_project, syn_folder.id, syn_folder.name, syn_folder]

    with pytest.raises(AttributeError):
        Synapsis.SynapseUtils.NOPE()


async def test_it_routes_from_synapsis(synapse_test_helper, syn_project, syn_folder):
    for dirpath, dirname, filename in Synapsis.SynapseUtils.walk(syn_project):
        assert dirpath[1] in [syn_project.id, syn_project.name, syn_project, syn_folder.id, syn_folder.name, syn_folder]

    for dirpath, dirname, filename in Synapsis.SynapseUtils.walk(Synapsis.Synapse, syn_project):
        assert dirpath[1] in [syn_project.id, syn_project.name, syn_project, syn_folder.id, syn_folder.name, syn_folder]

    async for dirpath, dirname, filename in Synapsis.Chain.SynapseUtils.walk(syn_project):
        assert dirpath[1] in [syn_project.id, syn_project.name, syn_project, syn_folder.id, syn_folder.name, syn_folder]

    with pytest.raises(AttributeError):
        Synapsis.SynapseUtils.NOPE()
