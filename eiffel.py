"""A Python Design By Contract module."""

import functools
import sys
import types


__all__ = ["Class", "__setattr__", "__delattr__", "routine", "require",
           "get_old"]
__version__ = "0.1.0"


# Class Invariant
# ===============
#
# To define a class that implement invariants, all public methods must be
# decorated with a function that invokes them and call the __invariant__
# method. That method is the one that has the assertions.
#
# __setattr__ and __delattr__ must also be overrided, because they change the
# state of the instance.


def _constraint_checker(function):
    @functools.wraps(function)
    def wrapper(self, *args, **kwargs):

        # Disable the constraint tester of __setattr__ and __delattr__
        # functions to ensure that __invariant__ are called only once, and
        # only after the method invocation.
        object.__setattr__(self, "_invariant_enabled", False)
        try:
            result = function(self, *args, **kwargs)
            self.__invariant__()  # check the contract
        finally:
            object.__setattr__(self, "_invariant_enabled", True)
        return result
    return wrapper


# I define __setattr__ and __delattr__ here
# because they will be part of the public API.


def __setattr__(self, name, value):
    """Assigns the value to the attribute, then
    check that the invariant are maintaned."""

    object.__setattr__(self, name, value)
    if self._invariant_enabled:
        self.__invariant__()


def __delattr__(self, name):
    """Delete the attribute, then check
    that the invariant are maintaned."""

    object.__delattr__(self, name)
    if self._invariant_enabled:
        self.__invariant__()


class Class:
    """Make a class that can define invariants."""

    _invariant_enabled = True

    # Override defaults methods with the new ones.
    __delattr__ = __delattr__
    __setattr__ = __setattr__

    def __invariant__(self):
        pass

    def __init_subclas__(cls):
        base_vars = vars(cls.__base__)
        for name, member in vars(cls).items():
            if name not in base_vars \
            and callable(member) \
            and not name.startswith("_"):  # noqa
                setattr(cls, name, _constraint_checker(member))
        super().__init_subclass__()


def routine(function):
    """A decorator that register the result of the function."""

    # NOTE 1: this object will be  filled by get_old function.
    __old__ = [{}]

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        __old__
        return function(*args, **kwargs)

    return wrapper


def get_old():
    """Return the local namespace of the last function call."""
    try:
        # function_frame is the namespace of the decorated function.
        function_frame = sys._getframe(1)

        # wrapper_locals is the namespace of the decorator.
        wrapper_locals = function_frame.f_back.f_locals

        # __old__ is the one indicated in NOTE 1
        if "__old__" not in wrapper_locals:
            function_name = function_frame.f_code.co_name
            raise ValueError(f"'{function_name}' function is not decorated"
                             " with 'eiffel.routine' decorator.")

        old = wrapper_locals["__old__"].pop()
        wrapper_locals["__old__"].append(function_frame.f_locals)

        return types.SimpleNamespace(**old) if old else None
    finally:
        del wrapper_locals
        del function_frame


class _Require:
    def __enter__(self):
        pass

    def __exit__(*args):
        pass


require = _Require()
