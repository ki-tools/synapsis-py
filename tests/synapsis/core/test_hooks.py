import pytest
from synapsis.core.hooks import Hooks
from synapsis import Synapsis


def test_it_adds_a_hook():
    assert Synapsis.Permissions.ADMIN
    hooks = Hooks()
    hooks.after_login(lambda hook: True)
    hooks.__add_hook__(hooks.AFTER_LOGIN, lambda hook: True)
    assert len(hooks.__hooks__) == 1
    assert len(hooks.__hooks__[hooks.AFTER_LOGIN]) == 2

    # Does not duplicate the hook/func.
    def callback(): pass

    hooks.after_login(callback)
    assert len(hooks.__hooks__[hooks.AFTER_LOGIN]) == 3
    hooks.after_login(callback)
    assert len(hooks.__hooks__[hooks.AFTER_LOGIN]) == 3


def test_it_clears_hooks():
    hooks = Hooks()
    hooks.after_login(lambda hook: True)
    hooks.after_login(lambda hook: True)
    assert len(hooks.__hooks__) == 1
    assert len(hooks.__hooks__[hooks.AFTER_LOGIN]) == 2
    hooks.clear()
    assert len(hooks.__hooks__) == 0


def test_it_calls_a_hook():
    hooks = Hooks()
    callbacks = []
    hooks.after_login(lambda hook: callbacks.append(1))
    hooks.after_login(lambda hook: callbacks.append(2))
    hooks.__call_hook__(hooks.AFTER_LOGIN)
    assert callbacks == [1, 2]
