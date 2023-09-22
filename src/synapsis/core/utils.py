from __future__ import annotations
import typing as t
import builtins
import inspect


class Utils:
    @classmethod
    def find(cls, iterable: iter, *args, **kwargs) -> t.Any:
        """
        Returns the first item in the iterable returning True or a default.
        Args:
            iterable:
            *args:
                Predicate is the first callable arg.
                Default value is the first arg that is not the predicate, otherwise None.

        Returns: Object
        """
        pred = cls.__parse_func__(*args, **kwargs)
        default = kwargs.get('default', None) or next(filter(lambda a: a != pred, args), None)
        return next(filter(pred, iterable), default)

    @classmethod
    def map(cls, *args, **kwargs) -> list[t.Any]:
        """
        Returns all the items in the iterable(s) mapped to from the function.
        Args:
            iterable(s):
            *args:
                Function is the first callable arg.
                Default value is the first arg that is not the function, otherwise [].

        Returns: List
        """
        func = cls.__parse_func__(*args, **kwargs)
        iterables = kwargs.get('iterables', None) or cls.select(args, lambda a: a != func and isinstance(a, t.Iterable))
        return list(builtins.map(func, *iterables))

    @classmethod
    def select(cls, iterable: iter, *args) -> list[t.Any]:
        """
        Returns all the items in the iterable returning True or a default.
        Args:
            iterable:
            *args:
                Predicate is the first callable arg.
                Default value is the first arg that is not the predicate, otherwise [].

        Returns: List
        """
        pred = cls.__parse_func__(*args)
        default = next(filter(lambda a: a != pred, args), [])
        return list(filter(pred, iterable)) or default

    @classmethod
    def first(cls, iterable: iter, *args) -> t.Any:
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
            return cls.find(iterable, *args)
        else:
            return iterable[0] if len(iterable) else None

    @classmethod
    def last(cls, iterable: iter, *args) -> t.Any:
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
            return cls.first(reversed_iterable, *args)
        else:
            return reversed_iterable[0] if len(reversed_iterable) else None

    @classmethod
    def __parse_func__(cls, *args, **kwargs):
        func = (kwargs.get('pred', None) or
                next(filter(lambda a: inspect.isfunction(a) or inspect.ismethod(a), args), None))
        return func
