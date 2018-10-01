"""Another Python Design By Contract implementation."""

import functools
import inspect
import types


__all__ = ["Class", "require", "body", "ensure", "Void", "routine"]


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


class _Statement:
    def __enter__(self):
        pass
    def __exit__(*args):
        pass


def _check_decorated_and_order(block_name):
    wrapper_locals = inspect.currentframe().f_back.f_back.f_back.f_locals
    if not "__result_object__" in wrapper_locals:
        function_frame = inspect.getouterframes(inspect.currentframe().f_back)
        current_function_name = function_frame[1].function
        raise ValueError(f"'{current_function_name}' function is not "
                          "decorated with 'eiffel.routine' decorator.")
    else:
        wrapper_locals["__block_order__"].append(block_name)
    return wrapper_locals["__block_order__"]


class _Require:
    def __enter__(self):
        __block_order__ = _check_decorated_and_order("require")
        if __block_order__.index("require") != 0:
            raise SyntaxError("'eiffel.require' must go before 'eiffel.body'.")

    def __exit__(self, *args):
        if "result" in inspect.currentframe().f_back.f_locals:
            raise NameError("'result' object must be defined inside "
                            "the 'eiffel.body' context manager.")


def _current_function_name():
    frames = inspect.getouterframes(inspect.currentframe().f_back.f_back)
    return ".".join(f.function for f in frames)


class _Body(_Statement):
    def __init__(self):
        self.old_locals = {}
        self.actual_locals = {}

    def __enter__(self):
        _check_decorated_and_order("body")

    def __exit__(self, *args):
        locals_ = inspect.currentframe().f_back.f_locals
        if 'result' not in locals_:
            raise NameError("'result' object is not defined.")
        name = _current_function_name()
        if name not in body.old_locals:
            void_locals = {key: Void for key in locals_.keys()}
            body.old_locals[name] = types.SimpleNamespace(**void_locals)
            body.actual_locals[name] = types.SimpleNamespace(**locals_)
        else:
            body.old_locals[name] = body.actual_locals[name]
            body.actual_locals[name] = types.SimpleNamespace(**locals_)

        wrapper_locals = inspect.currentframe().f_back.f_back.f_locals
        wrapper_locals["__result_object__"].append(locals_["result"])


class _Ensure:
    def __enter__(self):
        __block_order__ = _check_decorated_and_order("ensure")
        if not "body" in __block_order__:
            raise SyntaxError("'eiffel.ensure' must go after 'eiffel.body'.")
        name = _current_function_name()
        return body.old_locals[name]

    def __exit__(self, *args):
        if 'result' not in inspect.currentframe().f_back.f_locals:
            raise NameError("'result' object is not defined.")


require = _Require()
body = _Body()
ensure = _Ensure()


# A constant that indicates that the name is empty
Void = object()


def routine(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        __result_object__ = []
        __block_order__ = []
        function_output = function(*args, **kwargs)
        if not __result_object__:
            raise SyntaxError("Body block is not defined.")
        if __block_order__.count("require") > 1:
            raise SyntaxError("Only one 'eiffel.require' block are allowed.")
        if __block_order__.count("body") > 1:
            raise SyntaxError("Only one 'eiffel.body' block are allowed.")
        if __block_order__.count("ensure") > 1:
            raise SyntaxError("Only one 'eiffel.ensure' block are allowed.")
        if __result_object__[0] is not function_output:
            raise ValueError(
                "'result' object is not equal to function output.")
        return function_output
    return wrapper
