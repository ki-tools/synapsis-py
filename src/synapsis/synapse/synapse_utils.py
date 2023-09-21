from __future__ import annotations
import typing as t
import inspect
import synapseclient
import synapseutils
from . import Synapse


class SynapseUtils(object):
    __synapse__: Synapse

    def __init__(self, synapse: Synapse):
        self.__synapse__ = synapse

    def __getattr__(self, item: str) -> t.Any:
        attr = getattr(synapseutils, item)
        return SynapseutilsAttrWrapper(self.__synapse__, attr)


class SynapseutilsAttrWrapper:
    __synapse__: Synapse
    __attr__: t.Any

    def __init__(self, synapse: Synapse, attr: t.Any):
        self.__synapse__ = synapse
        self.__attr__ = attr

    def __getattr__(self, item):
        attr = getattr(synapseutils, item)
        return SynapseutilsAttrWrapper(self.__synapse__, attr)

    def __call__(self, *args, **kwargs):
        method = self.__attr__
        parameters = list(inspect.signature(method).parameters)
        if 'syn' in parameters and 'syn' not in kwargs:
            args = list(args)
            syn_index = parameters.index('syn')
            if len(args) >= syn_index + 1:
                syn = args[syn_index]
                if not isinstance(syn, (Synapse, synapseclient.Synapse)):
                    args.insert(syn_index, self.__synapse__)
            else:
                args.append(self.__synapse__)
            args = tuple(args)

        return self.__attr__(*args, **kwargs)
