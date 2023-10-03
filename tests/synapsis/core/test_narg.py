import pytest

from synapsis.core.narg import Narg, none


def test_it_works():
    obj_arg = object()
    str_arg = ''
    assert isinstance(Narg.arg, Narg)
    assert isinstance(none, Narg)

    assert Narg.arg == Narg.arg
    assert Narg.arg == none

    # Truthy
    assert not Narg.arg
    assert not none
    assert not (Narg.is_narg and none and None)

    for arg, is_narg in [
        [(Narg.arg,), True],
        [(none,), True],
        [(none, Narg.arg), True],

        [(none, obj_arg), False],
        [(None,), False],
        [(obj_arg,), False],
        [(None, obj_arg), False],
        [(none, Narg.arg, None, obj_arg), False]
    ]:
        assert Narg.is_narg(*arg) is is_narg

    for arg, is_none in [
        [(None,), True],
        [(None, None), True],
        [(Narg.arg,), False],
        [(none,), False],
        [(obj_arg,), False],
        [(str_arg,), False],
        [(None, str_arg,), False],
        [(str_arg, obj_arg, none, Narg.arg), False],
    ]:
        assert Narg.is_none(*arg) is is_none

    for arg, is_set in [
        [(obj_arg,), True],
        [(str_arg,), True],
        [(obj_arg, str_arg,), True],
        [(Narg.arg,), False],
        [(none,), False],
        [(None,), False],
        [(Narg.arg, none, None), False],
    ]:
        assert Narg.is_set(*arg) is is_set
        assert Narg.is_not_set(*arg) is not is_set

    for arg, is_not_set in [
        [(Narg.arg,), True],
        [(none,), True],
        [(None,), True],
        [(obj_arg, None), False],
        [(obj_arg,), False],
        [(obj_arg, str_arg), False]
    ]:
        assert Narg.is_not_set(*arg) is is_not_set
