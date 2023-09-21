from __future__ import annotations
import typing as t
from ..synapse import Synapse, SynapseUtils, SynapsePermission, SynapseConcreteType
from .synapsis_utils import SynapsisUtils
from . import utils
from dotchain import DotChain
from .lazy_readonly_property import LazyReadOnlyAttribute
import synapseclient
import numbers
from enum import Enum, auto


class Contexts(Enum):
    CHAIN = auto()
    PERMISSIONS = auto()
    CONCRETE_TYPES = auto()
    SYNAPSE = auto()
    SYNAPSE_UTILS = auto()
    UTILS = auto()


class Synapsis(object):

    def __lazy_factory__(self,
                         context: Contexts) -> TSynapsis | SynapsePermission | SynapseConcreteType | Synapse | SynapseUtils | SynapsisUtils:
        match context:
            case Contexts.CHAIN:
                return DotChain(data=self).With(self)
            case Contexts.PERMISSIONS:
                return SynapsePermission
            case Contexts.CONCRETE_TYPES:
                return SynapseConcreteType
            case Contexts.SYNAPSE:
                return Synapse()
            case Contexts.SYNAPSE_UTILS:
                return SynapseUtils(self.Synapse)
            case Contexts.UTILS:
                return SynapsisUtils(self.Synapse)

    Chain: t.Final[TSynapsis] = \
        LazyReadOnlyAttribute(__lazy_factory__, context=Contexts.CHAIN)

    Permissions: t.Final[SynapsePermission] = \
        LazyReadOnlyAttribute(__lazy_factory__, context=Contexts.PERMISSIONS, _singleton=True)

    ConcreteTypes: t.Final[SynapseConcreteType] = \
        LazyReadOnlyAttribute(__lazy_factory__, context=Contexts.CONCRETE_TYPES, _singleton=True)

    Synapse: t.Final[Synapse] = \
        LazyReadOnlyAttribute(__lazy_factory__, context=Contexts.SYNAPSE, _singleton=True)

    SynapseUtils: t.Final[SynapseUtils] = \
        LazyReadOnlyAttribute(__lazy_factory__, context=Contexts.SYNAPSE_UTILS, _singleton=True)

    Utils: t.Final[SynapsisUtils] = \
        LazyReadOnlyAttribute(__lazy_factory__, context=Contexts.UTILS, _singleton=True)

    utils: t.Final[utils] = utils

    def configure(self, synapse_args: dict = {}, **login_args: dict) -> t.Self:
        self.Synapse.__configure__(synapse_args=synapse_args, **login_args)
        return self

    def logged_in(self) -> bool:
        return self.Synapse.__logged_in__()

    def login(self) -> t.Self:
        self.Synapse.__login__()
        return self

    def logout(self, *args, **kwargs) -> t.Self:
        self.Synapse.logout(*args, **kwargs)
        return self

    def id_of(self, obj: synapseclient.Entity | str | dict | numbers.Number) -> str | numbers.Number:
        """
        Try to figure out the Synapse ID of the given object.

        :param obj: String, Entity object, or dictionary.
        :return: The ID or throws an exception.
        """
        return self.Utils.id_of(obj)

    def is_synapse_id(self, value: str, exists: bool = False) -> bool:
        """
        Gets if the value is a Synapse ID and optionally if the Entity exists.

        :param value: String to check.
        :param exists: Check if the Entity exists otherwise only validates the value is a Synapse ID.
        :return: True if the value matches the Synapse ID format otherwise False.
        """
        return self.Utils.is_synapse_id(value, exists=exists)

    def __getattr__(self, item):
        if hasattr(self.Synapse, item):
            return getattr(self.Synapse, item)
        raise AttributeError('Synapsis cannot find attribute: {0}'.format(item))


TSynapsis = t.TypeVar('TSynapsis', Synapsis, Synapse)
