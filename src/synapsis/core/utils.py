from __future__ import annotations
import typing as t
from collections.abc import Iterable
import builtins
import operator
from .narg import Narg, none


class Utils:
    @classmethod
    def find(cls,
             iterable: iter,
             *args,
             func: t.Callable = none,
             default: t.Any = None,
             key: str = none,
             value: t.Any = none) -> t.Any:
        """
        Gets the first item in the iterable returning True.
        Args:
            iterable: Items.
            func: Predicate. Or the first positional arg.
            default: Value to return if no items match the predicate.
            key: Name of the attribute to check.
            value: Value to match.

        Returns: Object
        """
        return next(cls.__build_filter__(iterable, *args, func=func, key=key, value=value), default)

    @classmethod
    def select(cls,
               iterable: iter,
               *args,
               func: t.Callable = none,
               key: str = none,
               value: t.Any = none) -> list[t.Any]:
        """
        Gets all the items in the iterable returning True.
        Args:
            iterable: Items.
            func: Predicate. Or the first positional arg.
            key: Name of the attribute to check.
            value: Value to match.

        Returns: List
        """
        return list(cls.__build_filter__(iterable, *args, func=func, key=key, value=value))

    @classmethod
    def first(cls,
              iterable: iter,
              *args,
              func: t.Callable = none,
              default: t.Any = None,
              key: str = none,
              value: t.Any = none) -> t.Any:
        """
        Gets the first item in the iterable, or the first item returning True.
        Args:
            iterable: Items.
            func: Predicate. Or the first positional arg.
            default: Value to return if no items match the predicate.
            key: Name of the attribute to check.
            value: Value to match.

        Returns: Object
        """
        return next(
            cls.__build_filter__(iterable, *args,
                                 func=func, key=key, value=value, default_func=cls.__always_true__),
            default)

    @classmethod
    def last(cls,
             iterable: iter,
             *args,
             func: t.Callable = none,
             default: t.Any = None,
             key: str = none,
             value: t.Any = none) -> t.Any:
        """
        Gets the last item in the iterable, or the last item returning True.
        Args:
            iterable: Items.
            func: Predicate. Or the first positional arg.
            default: Value to return if no items match the predicate.
            key: Name of the attribute to check.
            value: Value to match

        Returns: Object
        """
        reversed_iterable = iterable and iterable[::-1]
        return next(
            cls.__build_filter__(reversed_iterable, *args,
                                 func=func, key=key, value=value, default_func=cls.__always_true__),
            default)

    @classmethod
    def map(cls,
            *iterables,
            func: t.Callable = none,
            key: str = none) -> list[t.Any]:
        """
        Gets all the items in the iterable(s) mapped.
        Args:
            func: Callable to transform each item. Or the last positional arg.
            key: Name of the attribute to map.
            iterables: List of iterables.

        Returns: List
        """
        if not func and len(iterables) > 1:
            func = iterables[-1]
            iterables = iterables[:-1]

        if Narg.is_set(key):
            if func:
                _orig_func = func
                func = lambda i: _orig_func(cls.__getattr_by_key__(i, key))
            else:
                func = lambda i: cls.__getattr_by_key__(i, key)

        if Narg.is_narg(func):
            func = None

        return list(builtins.map(func, *iterables))

    @classmethod
    def unique(cls,
               iterable: iter,
               *args,
               func: t.Callable = none,
               key: str = none) -> list[t.Any]:
        """
        Gets a list of unique items in the iterable.
        Args:
            iterable: Items.
            func: Callable to return a value to check for uniqueness. Or the first positional arg.
            key: Name of the attribute to get the value from to check for uniqueness.

        Returns: Object
        """
        if not func and len(args):
            func = args[0]

        if Narg.is_set(key):
            if func:
                _orig_func = func
                func = lambda i: _orig_func(cls.__getattr_by_key__(i, key))
            else:
                func = lambda i: cls.__getattr_by_key__(i, key)

        results = []
        uniq_values = []
        for item in iterable:
            if func:
                value = func(item)
                if operator.countOf(uniq_values, value) == 0:
                    results.append(item)
                    uniq_values.append(value)
            else:
                if operator.countOf(results, item) == 0:
                    results.append(item)

        return results

    @classmethod
    def __build_filter__(cls,
                         iterable: iter,
                         *args,
                         func: t.Callable = none,
                         default_func: t.Callable = None,
                         key: str = none,
                         value: t.Any = none) -> t.Any:
        """
        Builds an iterable filter.
        Args:
            iterable: Items.
            func: Predicate. Or the first positional arg.
            default_func: Predicate to use if func is not set or found.
            key: Name of the attribute to check.
            value: Value to match.

        Returns: Object
        """
        if not func and len(args):
            func = args[0]

        if Narg.is_set(key, value):
            if func:
                _orig_func = func
                func = lambda i: _orig_func(cls.__getattr_by_key__(i, key)) == value
            else:
                func = lambda i: cls.__getattr_by_key__(i, key) == value
        elif Narg.is_set(key):
            if func:
                _orig_func = func
                func = lambda i: _orig_func(cls.__getattr_by_key__(i, key))
            else:
                func = lambda i: cls.__getattr_by_key__(i, key)
        elif Narg.is_set(value):
            if func:
                _orig_func = func
                func = lambda i: _orig_func(i) == value
            else:
                func = lambda i: i == value

        if not func:
            func = default_func

        if Narg.is_narg(func):
            func = None

        return filter(func, iterable)

    @classmethod
    def __getattr_by_key__(cls, obj, key):
        if isinstance(obj, Iterable) and key in obj:
            return obj[key]
        else:
            return getattr(obj, key)

    @classmethod
    def __always_true__(cls, *args, **kwargs):
        return True
