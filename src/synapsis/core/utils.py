from __future__ import annotations
import typing as t
import builtins
import inspect


def find(iterable: iter, *args, **kwargs) -> t.Any:
    """
    Returns the first item in the iterable returning True or a default.
    Args:
        iterable:
        *args:
            Predicate is the first callable arg.
            Default value is the first arg that is not the predicate, otherwise None.

    Returns: Object
    """
    pred = __parse_func__(*args, **kwargs)
    default = kwargs.get('default', None) or next(filter(lambda a: a != pred, args), None)
    return next(filter(pred, iterable), default)


def map(*args, **kwargs) -> list[t.Any]:
    """
    Returns all the items in the iterable(s) mapped to from the function.
    Args:
        iterable(s):
        *args:
            Function is the first callable arg.
            Default value is the first arg that is not the function, otherwise [].

    Returns: List
    """
    func = __parse_func__(*args, **kwargs)
    iterables = kwargs.get('iterables', None) or select(args, lambda a: a != func and isinstance(a, t.Iterable))
    return list(builtins.map(func, *iterables))


def select(iterable: iter, *args) -> list[t.Any]:
    """
    Returns all the items in the iterable returning True or a default.
    Args:
        iterable:
        *args:
            Predicate is the first callable arg.
            Default value is the first arg that is not the predicate, otherwise [].

    Returns: List
    """
    pred = __parse_func__(*args)
    default = next(filter(lambda a: a != pred, args), [])
    return list(filter(pred, iterable)) or default


def first(iterable: iter, *args) -> t.Any:
    """
    Returns the first item in the iterable or a default.
    Args:
        iterable:
        *args:
            Predicate is the first callable arg.
            Default value is the first arg that is not the predicate, otherwise None.

    Returns: Object
    """
    if len(args):
        return find(iterable, *args)
    else:
        return iterable[0] if len(iterable) else None


def last(iterable: iter, *args) -> t.Any:
    """
    Returns the last item in the iterable or a default.
    Args:
        iterable:
        *args:
            Predicate is the first callable arg.
            Default value is the first arg that is not the predicate, otherwise None.

    Returns: Object
    """
    reversed_iterable = iterable[::-1]
    if len(args):
        return first(reversed_iterable, *args)
    else:
        return reversed_iterable[0] if len(reversed_iterable) else None


def __parse_func__(*args, **kwargs):
    func = kwargs.get('pred', None) or next(filter(lambda a: inspect.isfunction(a) or inspect.ismethod(a), args), None)
    return func
