"""A Python Design By Contract module."""


__all__ = ["Class", "__setattr__", "__delattr__", "routine", "require", "old"]
__version__ = "0.3.4"


if __debug__:
    from .debugimpl import *
else:
    from .optimizedimpl import *
