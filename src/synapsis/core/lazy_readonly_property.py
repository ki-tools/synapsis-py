from __future__ import annotations
import typing as t
import inspect
from . import utils


class LazyReadOnlyAttribute(object):
    fget: callable
    fget_args: tuple
    fget_kwargs: dict
    _fget_parameters: list[str]
    singleton: bool
    context: t.Any
    instance: t.Any

    ATTR_NAME_ARG: t.Final[t.ClassVar[str]] = '{__ATTR_NAME__}'

    def __init__(self,
                 fget: callable,
                 *args: t.Optional[tuple],
                 _singleton: t.Optional[bool] = False,
                 _context: t.Optional[t.Any] = None,
                 **kwargs: t.Optional[dict],
                 ):
        self.fget = fget
        self.fget_args = args
        self.fget_kwargs = kwargs
        self._fget_parameters = None
        self.singleton = _singleton
        self.context = _context
        self.instance = None

    def __get__(self, instance, owner):
        if self.singleton and self.instance is not None:
            return self.instance

        fget, fget_args, fget_kwargs = self.__prepare_get__(instance, owner)
        result = fget(*fget_args, **fget_kwargs)

        if self.singleton:
            self.instance = result
        return result

    def __prepare_get__(self, instance, owner):
        fget = self.fget
        fget_args = self.fget_args

        if self._fget_parameters is None:
            if not isinstance(fget, t.Callable):
                fget = fget.__get__(instance, owner)
            try:
                self._fget_parameters = list(inspect.signature(fget).parameters)
            except ValueError:
                pass

        requires_cls = self._fget_parameters and utils.first(self._fget_parameters) == 'cls'
        requires_self = self._fget_parameters and utils.first(self._fget_parameters) == 'self'
        first_arg = (owner or instance) if requires_cls else (instance or owner) if requires_self else None
        if first_arg is not None and not fget_args or len(fget_args) > 1 and fget_args[0] != first_arg:
            fget_args = (first_arg,) + fget_args

        if self.ATTR_NAME_ARG in fget_args:
            if not requires_self:
                name, attr = self.find(owner or instance, lazy_attr=self)
            else:
                name, attr = self.find(instance or owner, lazy_attr=self)

            if attr is not None:
                fget_args = tuple(name if a == self.ATTR_NAME_ARG else a for a in list(fget_args))
            else:
                raise AttributeError('Could not find lazy attribute name for: {0}'.find(self))

        return (fget, fget_args, self.fget_kwargs)

    @classmethod
    def find(cls,
             obj: t.Any,
             lazy_attr: LazyReadOnlyAttribute = None
             ) -> tuple(str, LazyReadOnlyAttribute) | list[tuple(str, LazyReadOnlyAttribute)]:
        obj_vars = vars(obj).items()
        if lazy_attr:
            result = utils.find(obj_vars, lambda a: a[1] == lazy_attr)
        else:
            result = utils.select(obj_vars, lambda a: isinstance(a[1], cls))
        return result
