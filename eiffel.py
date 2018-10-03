"""A Python Design By Contract module."""

import functools
import inspect
import types


__all__ = ["Class", "require", "body", "ensure", "VOID", "routine",
           "__setattr__", "__delattr__"]


def __setattr__(self, name, value):
    """Implement setattr(self, name, value)."""

    if self._check_constraint:
        object.__setattr__(self, name, value)
        self.__invariant__()
    else:
        object.__setattr__(self, name, value)


def __delattr__(self, name):
    """Implement delattr(self, name)."""
    if self._check_constraint:
        object.__delattr__(self, name)
        self.__invariant__()
    else:
        object.__delattr__(self, name)


class _MetodWrapperMeta(type):
    def __call__(cls, *args, **kwargs):
        subclass = super().__call__(*args, **kwargs)
        object.__setattr__(subclass, "_check_constraint", True)

        for name, member in inspect.getmembers(cls):
            if callable(member) \
            and not name.startswith("_") \
            and not (name.startswith("__") and name.endswith("__")):

                @functools.wraps(member)
                def wrapper(self, *args, **kwargs):
                    object.__setattr__(self, "_check_constraint", False)
                    try:
                        result = member(self, *args, **kwargs)
                        self.__invariant__()
                    finally:
                        object.__setattr__(self, "_check_constraint", True)
                    return result
                setattr(cls, name, wrapper)

        setattr(cls, "__setattr__", __setattr__)
        setattr(cls, "__delattr__", __delattr__)
        subclass.__invariant__()
        return subclass


class Class(metaclass=_MetodWrapperMeta):
    """Make a class that can define invariants."""

    def __invariant__(self):
        pass


# Returns the function namespace and the wrapper namespace. Check if the
# function is decorated. Finally register the context manager used.
def _get_locals_and_register(block_name):
    function_frame = inspect.currentframe().f_back.f_back
    wrapper_locals = function_frame.f_back.f_locals
    if not "__block_used__" in wrapper_locals:
        function_name = inspect.getframeinfo(function_frame).function
        raise ValueError(f"'{function_name}' function is not "
                          "decorated with 'eiffel.routine' decorator.")
    wrapper_locals["__block_used__"].append(block_name)
    function_locals = function_frame.f_locals
    return wrapper_locals, function_locals


class _ExitMethod:
    def __exit__(self, *args):
        pass


class _Require(_ExitMethod):
    def __enter__(self):
        wrapper_locals, _ = _get_locals_and_register("require")
        if wrapper_locals["__block_used__"].index("require") != 0:
            raise SyntaxError("'eiffel.require' must go before 'eiffel.body'.")


class _Body:
    def __init__(self):
        self.old_locals = {}
        self.actual_locals = {}

    def __enter__(self):
        pass

    def __exit__(self, *args):
        wrapper_locals, function_locals = _get_locals_and_register("body")
        if "result" not in function_locals:
            raise SyntaxError("'result' object is not defined.")
        wrapper_locals["__result_object__"].append(function_locals["result"])
        name = wrapper_locals["function"].__qualname__
        if name not in body.old_locals:
            body.old_locals[name] = VOID
        else:
            body.old_locals[name] = body.actual_locals[name]
        body.actual_locals[name] = types.SimpleNamespace(**function_locals)


class _Ensure(_ExitMethod):
    def __enter__(self):
        wrapper_locals, _ = _get_locals_and_register("ensure")
        if not "body" in wrapper_locals["__block_used__"]:
            raise SyntaxError("'eiffel.ensure' must go after 'eiffel.body'.")
        name = wrapper_locals["function"].__qualname__
        return body.old_locals[name]


require = _Require()
body = _Body()
ensure = _Ensure()


# A constant that indicates that the name is empty
VOID = object()


def routine(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        __result_object__ = []
        __block_used__ = []
        function_output = function(*args, **kwargs)
        if not __result_object__:
            raise SyntaxError("Body block is not defined.")
        if __block_used__.count("require") > 1:
            raise SyntaxError("Only one 'eiffel.require' block are allowed.")
        if __block_used__.count("body") > 1:
            raise SyntaxError("Only one 'eiffel.body' block are allowed.")
        if __block_used__.count("ensure") > 1:
            raise SyntaxError("Only one 'eiffel.ensure' block are allowed.")
        if __result_object__[0] is not function_output:
            raise ValueError(
                "'result' object is not equal to function output.")
        return function_output
    return wrapper
