from __future__ import annotations
import typing as t


class Hooks:
    AFTER_LOGIN: t.Final[str] = 'AFTER_LOGIN'
    ALL_HOOKS: t.Final[list[str]] = [AFTER_LOGIN]

    def __init__(self):
        self.__hooks__ = {}

    def after_login(self, func: t.Callable):
        self.__add_hook__(self.AFTER_LOGIN, func)

    def clear(self):
        self.__hooks__.clear()

    def __add_hook__(self, hook: str, func: t.Callable):
        if hook not in self.ALL_HOOKS:
            raise ValueError('Invalid hook: {0}. Must be one of: {1}.'.format(hook, ', '.join(self.ALL_HOOKS)))
        if hook not in self.__hooks__:
            self.__hooks__[hook] = []
        self.__hooks__[hook].append(func)

    def __call_hook__(self, hook):
        funcs = self.__hooks__.get(hook, [])
        for func in funcs:
            func(hook=hook)
