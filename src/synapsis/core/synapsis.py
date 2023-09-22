from __future__ import annotations
import typing as t
from ..synapse import Synapse, SynapseUtils, SynapsePermission, SynapseConcreteType
from .utils import Utils
from .synapsis_utils import SynapsisUtils
from .hooks import Hooks
from dotchain import DotChain
import synapseclient
import numbers


class Synapsis(object):
    def __init__(self):
        self._hooks: Hooks = Hooks()
        self._synapse: Synapse = Synapse()
        self._synapse_utils: SynapseUtils = SynapseUtils(self._synapse)
        self._synapsis_utils: SynapsisUtils = SynapsisUtils(self._synapse)

    Chain: TSynapsis = property(lambda self: DotChain(data=self).With(self))
    Permissions: t.Type[SynapsePermission] = property(lambda self: SynapsePermission)
    ConcreteTypes: t.Type[SynapseConcreteType] = property(lambda self: SynapseConcreteType)
    Synapse: Synapse = property(lambda self: self._synapse)
    SynapseUtils: SynapseUtils = property(lambda self: self._synapse_utils)
    Utils: SynapsisUtils = property(lambda self: self._synapsis_utils)
    utils: t.Type[Utils] = property(lambda self: Utils)
    hooks: Hooks = property(lambda self: self._hooks)

    def configure(self, synapse_args: dict = {}, **login_args: dict) -> t.Self:
        self.Synapse.__configure__(synapse_args=synapse_args, **login_args)
        return self

    def logged_in(self) -> bool:
        return self.Synapse.__logged_in__()

    def login(self) -> t.Self:
        self.Synapse.__login__(hooks=self.hooks)
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
