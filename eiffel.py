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


def _set_attribute(self, name, value):
    old_value = getattr(self, name)
    if self._check_constraint:
        object.__setattr__(self, name, value)
        try:
            self.__invariant__()
        except AssertionError:
            object.__setattr__(self, name, old_value)
            raise
    else:
        self._previous_state.append((name, old_value))
        object.__setattr__(self, name, value)


class _MetodWrapperMeta(type):
    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        object.__setattr__(obj, "_check_constraint", True)

        for name, member in inspect.getmembers(cls):
            if callable(member) \
            and not name.startswith("_") \
            and not (name.startswith("__") and name.endswith("__")):

                @functools.wraps(member)
                def wrapper(self, *args, **kwargs):
                    object.__setattr__(self, "_check_constraint", False)
                    object.__setattr__(self, "_previous_state", [])
                    try:
                        result = member(self, *args, **kwargs)
                        self.__invariant__()
                    except AssertionError:
                        for name, value in reversed(self._previous_state):
                            object.__setattr__(self, name, value)
                        raise
                    finally:
                        object.__setattr__(self, "_check_constraint", True)
                    return result
                setattr(cls, name, wrapper)

        setattr(cls, "__setattr__", _set_attribute)
        obj.__invariant__()
        return obj


class Class(metaclass=_MetodWrapperMeta):
    """Make a class that can define invariants."""

    def __invariant__(self):
        pass
