"""Another Python Design By Contract implementation."""

import functools
import inspect


__all__ = ["Routine", "Class"]


class _RoutineMeta(type):
    def __call__(cls, *args, **kwargs):
        cls.require(*args, **kwargs)
        result = cls.do(*args, **kwargs)
        cls.ensure(result)
        return result

    def require(cls, *args, **kwargs):
        pass

    def ensure(cls, result):
        pass


class Routine(metaclass=_RoutineMeta):
    """Make a class that behaves like a function with constrains."""
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "do"):
            raise NotImplementedError("Method 'do' is not defined.")

# Add checkers
class _MetodWrapperMeta(type):
    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        for name, member in inspect.getmembers(cls):
            if callable(member) \
            and not name.startswith("__") \
            and not name.endswith("__"):
                @functools.wraps(member)
                def wrapper(self, *args, **kwargs):
                    result = member(self, *args, **kwargs)
                    self.__invariant__()
                    return result
                setattr(cls, name, wrapper)
        obj.__invariant__()  # check after object initialization
        return obj


class Class(metaclass=_MetodWrapperMeta):
    """Make a class that can define invariants."""

    def __invariant__(self):
        pass
