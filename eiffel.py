"""A Python Design By Contract module."""

import functools
import sys
import types
from typing import Callable, Any, Optional


__all__ = ["Class", "__setattr__", "__delattr__", "routine", "require", "old"]
__version__ = "0.3.0"


# Class Invariant
# ===============
#
# To define a class that implement invariants, all public methods must be
# decorated with a function that invokes them and call the __invariant__
# method. That method is the one that has the assertions.
#
# __setattr__ and __delattr__ must also be overrided, because they change the
# state of the instance.

TKwArgs = dict[str, Any]
TArgs = tuple[Any]


def _constraint_checker(
    function: Callable[..., Any]
) -> Callable[[Any], Any]:
    @functools.wraps(function)
    def wrapper(self: Any, *args: TArgs, **kwargs: TKwArgs) -> Any:

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


def __setattr__(self: Any, name: str, value: Any) -> None:
    """Assigns the value to the attribute, then
    check that the invariant are maintaned."""

    object.__setattr__(self, name, value)
    if self._invariant_enabled:
        self.__invariant__()


def __delattr__(self: Any, name: str) -> None:
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

    def __invariant__(self) -> None:
        pass

    def __init_subclas__(cls) -> None:
        base_vars = vars(cls.__base__)  # type: ignore[attr-defined]
        for name, member in vars(cls).items():
            if name not in base_vars \
            and callable(member) \
            and not name.startswith("_"):  # noqa
                setattr(cls, name, _constraint_checker(member))
        super().__init_subclass__()


def routine(function: Callable[..., Any]) -> Callable[..., Any]:
    """A decorator that register the result of the function."""

    # NOTE 1: this object will be  filled by get_old function.
    __old__: list[dict[str, Any]] = [{}]

    @functools.wraps(function)
    def wrapper(*args: TArgs, **kwargs: TKwArgs) -> Any:
        result = __old__[0]["__result__"] = function(*args, **kwargs)
        return result

    return wrapper


class _Require:
    def __enter__(self) -> None:
        pass

    def __exit__(*args) -> None:
        pass


require = _Require()


class _Old:
    def __bool__(self) -> bool:
        """Lookup the local namespace of the last function call."""
        try:
            # function_frame is the namespace of the decorated function.
            function_frame: Optional[types.FrameType] = sys._getframe(1)

            if function_frame is not None:
                function_name = function_frame.f_code.co_name

                # wrapper_locals is the namespace of the decorator.
                wrapper_locals = function_frame\
                    .f_back.f_locals  # type: ignore[union-attr]

                # __old__ is the one indicated in NOTE 1
                if "__old__" not in wrapper_locals:
                    raise ValueError(
                        f"'{function_name}' function is not decorated"
                        " with 'eiffel.routine' decorator.")

                locals_ = wrapper_locals["__old__"].pop()
                wrapper_locals["__old__"].append(function_frame.f_locals)
                if locals_:
                    for name, value in locals_.items():
                        setattr(self, name, value)
                    return True

            return False
        finally:
            del wrapper_locals
            del function_frame


old = _Old()
