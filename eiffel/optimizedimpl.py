"""Optimized mode implementation"""

from typing import Callable, Any, Dict, Tuple


__all__ = ["Class", "__setattr__", "__delattr__", "routine", "require", "old"]

TKwArgs = Dict[str, Any]
TArgs = Tuple[Any]


__setattr__ = object.__setattr__
__delattr__ = object.__delattr__


class Class:
    """Make a class that can define invariants."""


def routine(function: Callable[..., Any]) -> Callable[..., Any]:
    """A decorator that register the result of the function."""

    return function


class _Require:
    def __enter__(self) -> None:
        pass

    def __exit__(*args) -> None:
        pass


require = _Require()


class _Old:
    def __bool__(self) -> bool:
        """Lookup the local namespace of the last function call."""
        return False


old = _Old()
