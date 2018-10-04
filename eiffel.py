"""A Python Design By Contract module."""

import functools
import inspect
import types


__all__ = ["Class", "require", "body", "ensure", "VOID", "routine",
           "__setattr__", "__delattr__"]


# Class Invariant
# ===============
#
# To define a class that implement invariants, all public methods must be
# decorated with a function that invokes them, and then call the
# __invariant__ method. That method is the one that has the assertions.
#
# __setattr__ and __delattr__ must also be overrided, because they change the
# state of the instance.


class _ConstraintCheckerMeta(type):

    # Remember that when __init__ is called, the class object
    # already exists and is given by the 'cls' argument.
    def __init__(cls, name, bases, namespace):
        for name, member in inspect.getmembers(cls):
            if callable(member) and not name.startswith("_"):
                @functools.wraps(member)
                def constraint_checker(self, *args, **kwargs):

                    # Disable the constraint tester of __setattr__ and
                    # __delattr__ functions to ensure that __invariant__ are
                    # called only once, and only after the method invocation.
                    object.__setattr__(self, "_invariant_enabled", False)
                    try:
                        result = member(self, *args, **kwargs)
                        self.__invariant__()  # check the contract
                    finally:
                        object.__setattr__(self, "_invariant_enabled", True)
                    return result

                # Assign the decorated method to the class
                setattr(cls, name, constraint_checker)

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

    # Override the defaults methods with the new ones.
    __delattr__ = __delattr__
    __setattr__ = __setattr__

    def __invariant__(self):
        pass


# Preconditions and Postconditions
# ================================
#
# Functions constrains are done by the colaborative work between the
# context managers and the decorator.
#
# 'require', 'body' and 'ensure' are context managers (see NOTE 4).
# 'routine' is the decorator (see NOTE 1).
#
# Context managers get inside the decorator namespace and modify
# '__result_object__' and '__block_used__' variables.


# NOTE 1: the 'function' argument is the function referenced in NOTE 3.
def routine(function):
    """A decorator that analyze and ensure the correct
    syntax of the constrains defined on the function."""

    # NOTE 2: the following function is the wrapper referenced in NOTE 3.
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        __result_object__ = []
        __block_used__ = []

        # NOTE 5: Context managers on the body of 'function' get inside this
        # current namespace and fill '__result_object__' and '__block_used__'
        # variables.
        function_output = function(*args, **kwargs)

        # Now I can analyze the content of the function with the informacion
        # provided:
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

        # If all is right, return the result of the function
        return function_output
    return wrapper


# NOTE 3: returns the 'function' local namespace (see NOTE 1) and the 'wrapper'
# local namespace (see NOTE 2). Check if the function is decorated. Finally
# register the context manager used.
def _get_locals_and_register(context_manager_name):

    # The frame of the decorated function (see NOTE 2)
    function_frame = inspect.currentframe().f_back.f_back

    # The local namespace of the wrapper (see NOTE 1)
    wrapper_locals = function_frame.f_back.f_locals

    # Check if the function is decorated
    if not "__block_used__" in wrapper_locals:
        function_name = inspect.getframeinfo(function_frame).function
        raise ValueError(f"'{function_name}' function is not "
                          "decorated with 'eiffel.routine' decorator.")

    # Register the name of the context manager used.
    wrapper_locals["__block_used__"].append(context_manager_name)

    # The local namespace of the decorated function (see NOTE 2)
    function_locals = function_frame.f_locals

    return wrapper_locals, function_locals


class _ExitMethod:
    def __exit__(self, *args):
        pass


class _Require(_ExitMethod):
    def __enter__(self):
        wrapper_locals, _ = _get_locals_and_register("require")

        # '__block_used__' was filled with the "require" string by
        # the _get_locals_and_register funtion.
        if wrapper_locals["__block_used__"].index("require") != 0:
            raise SyntaxError("'eiffel.require' must go before 'eiffel.body'.")


# A constant that indicates that a name is empty.
VOID = object()


class _Body:
    def __init__(self):

        # Stores function local namespace of the last function call (the 'old'
        # object). The key is the decorated function __qualname__, and the
        # value are a types.SimpleNamespace that stores the namespace.
        self.old_locals = {}

        # Like self.old_locals but with the current data.
        self.actual_locals = {}

    def __enter__(self):
        pass

    def __exit__(self, *args):
        wrapper_locals, function_locals = _get_locals_and_register("body")
        if "result" not in function_locals:
            raise SyntaxError("'result' object is not defined.")
        wrapper_locals["__result_object__"].append(function_locals["result"])

        # Creates the 'old' object
        name = wrapper_locals["function"].__qualname__

        # body.old_locals[name] is the 'old' object
        if name not in body.old_locals:
            body.old_locals[name] = VOID
        else:
            body.old_locals[name] = body.actual_locals[name]
        body.actual_locals[name] = types.SimpleNamespace(**function_locals)


class _Ensure(_ExitMethod):
    def __enter__(self):
        wrapper_locals, _ = _get_locals_and_register("ensure")

        # '__block_used__' was filled with the "ensure" string by
        # the _get_locals_and_register funtion.
        if not "body" in wrapper_locals["__block_used__"]:
            raise SyntaxError("'eiffel.ensure' must go after 'eiffel.body'.")
        name = wrapper_locals["function"].__qualname__

        # Returns the 'old' object
        return body.old_locals[name]


# NOTE 4: Create all context managers
require = _Require()
body = _Body()
ensure = _Ensure()
