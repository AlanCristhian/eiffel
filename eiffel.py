"""A Python Design By Contract module."""

import functools
import sys
import types
from typing import Callable, Any, Optional, Dict, Tuple


__all__ = ["Class", "__setattr__", "__delattr__", "routine", "require", "old"]
__version__ = "0.3.4"

TKwArgs = Dict[str, Any]
TArgs = Tuple[Any]
SetAttrType = Callable[[Any, str, Any], None]
DelAttrType = Callable[[Any, str], None]


# Class Invariant
# ===============
#
# To define a class that implement invariants, all public methods must be
# decorated with a function that invokes them and call the __invariant__
# method. That method is the one that has the assertions.
#
# __setattr__ and __delattr__ must also be overrided, because they change the
# state of the instance.


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

if __debug__:
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
else:
    __setattr__: SetAttrType = object.__setattr__  # type: ignore[no-redef]
    __delattr__: DelAttrType = object.__delattr__  # type: ignore[no-redef]


class Class:
    """Make a class that can define invariants."""

    if __debug__:
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

    if not __debug__:
        return function

    # NOTE 1: this object will be  filled by get_old function.
    __old__: list[TKwArgs] = [{}]

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
    namespace: Dict[int, TKwArgs] = {}

    def __bool__(self) -> bool:
        """Lookup the local namespace of the last function call."""
        if not __debug__:
            return False

        # function_frame is the namespace of the decorated function.
        function_frame: Optional[types.FrameType] = sys._getframe(1)

        if function_frame:

            # wrapper_locals is the namespace of the decorator.
            wrapper_locals = function_frame\
                .f_back.f_locals  # type: ignore[union-attr]

            # __old__ is the one indicated in NOTE 1
            old_locals = wrapper_locals.get("__old__")
            if old_locals is None:
                function_name = function_frame.f_code.co_name
                raise ValueError(
                    f"'{function_name}' function is not decorated"
                    " with 'eiffel.routine' decorator.")

            locals_, old_locals[0] = old_locals[0], function_frame.f_locals
            if locals_:
                self.namespace[id(function_frame)] = locals_
                return True

        return False

    def __getattr__(self, name: str) -> Any:
        function_frame: Optional[types.FrameType] = sys._getframe(1)
        if function_frame:
            function_locals = self.namespace.get(id(function_frame))
            if function_locals and name in function_locals:
                return function_locals[name]
        raise ValueError(
            r"'old' has no attributes. Wrap your postconditions "
            r"inside an 'if eiffel.old:' statement.")


old = _Old()
