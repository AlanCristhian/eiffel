"""A Python Design By Contract module."""

import functools
import inspect
import types


__all__ = ["Class", "__setattr__", "__delattr__", "routine", "require"]


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


class _ConstraintCheckerMeta(type):

    # Remember that when __init__ is called, the class object
    # already exists and is given by the 'cls' argument.
    def __init__(cls, name, bases, namespace):
        for name, member in inspect.getmembers(cls):
            if callable(member) and not name.startswith("_"):
                setattr(cls, name, _constraint_checker(member))

    # Instantiate the class, check the constraint and returns the instance
    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        instance.__invariant__()
        return instance


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


class Class(metaclass=_ConstraintCheckerMeta):
    """Make a class that can define invariants."""

    _invariant_enabled = True

    # Override defaults methods with the new ones.
    __delattr__ = __delattr__
    __setattr__ = __setattr__

    def __invariant__(self):
        pass


def routine(function):
    """A decorator that register the result of the function."""

    __old__ = None

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        nonlocal __old__

        # NOTE 1: '__locals__' will be filled by 'function'
        # if they call the 'get_last' function.
        __locals__ = []
        result = function(*args, **kwargs)

        # If '__locals__' it's not empty, 'get_last'
        # has been called by 'function'
        if __locals__:
            # Update the value of __old__
            old_locals = {**__locals__[0], **{"__result__": result}}
            __old__ = types.SimpleNamespace(**old_locals)
        return result

    return wrapper


def get_last():
    """Return the local namespace of the last function call."""

    function_frame = inspect.currentframe().f_back
    wrapper_locals = function_frame.f_back.f_locals

    if "__locals__" not in wrapper_locals \
    and "__old__" not in wrapper_locals:
        function_name = inspect.getframeinfo(function_frame).function
        raise ValueError(f"'{function_name}' function is not decorated with "
                          "'eiffel.routine' decorator.")

    # '__locals__' is the one indicated in NOTE 1 and 'function_frame.f_locals'
    # is the local namespace of the decorated function.
    wrapper_locals["__locals__"].append(function_frame.f_locals)

    return wrapper_locals["__old__"]


class _Require:
    def __enter__(self):
        pass

    def __exit__(*args):
        pass


require = _Require()
