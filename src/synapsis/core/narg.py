class NargMeta(type):
    __INSTANCE__ = None

    @property
    def arg(cls):
        if cls.__INSTANCE__ is None:
            cls.__INSTANCE__ = Narg()
        return cls.__INSTANCE__


class Narg(object, metaclass=NargMeta):
    __slots__ = tuple()

    def __bool__(self):
        return False

    @classmethod
    def is_none(cls, *values):
        return all(value is None for value in values)

    @classmethod
    def is_narg(cls, *values):
        return all(isinstance(value, cls) for value in values)

    @classmethod
    def is_not_set(cls, *values):
        return all(cls.is_none(value) or cls.is_narg(value) for value in values)

    @classmethod
    def is_set(cls, *values):
        return all(not cls.is_none(value) and not cls.is_narg(value) for value in values)


none = Narg.arg
