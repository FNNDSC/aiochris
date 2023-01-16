"""
Metaprogramming helper functions.
"""
import typing
from typing import Type, Callable, TypeVar, ForwardRef, Optional

import typing_inspect

_T = TypeVar("_T")


def get_return_hint(fn: Callable[[...], _T]) -> Type[_T]:
    hints = typing.get_type_hints(fn)
    if "return" not in hints:
        raise ValueError(f"Function {fn} must define a return type hint.")
    return hints["return"]


def generic_of(c: Type, t: Type[_T], subclass=False) -> Optional[Type[_T]]:
    """
    Get the actual class represented by a bound TypeVar of a generic.
    """
    for generic_type in typing_inspect.get_args(c):
        if isinstance(generic_type, (str, ForwardRef, TypeVar)):
            continue
        if issubclass(generic_type, t):
            return generic_type

    if hasattr(c, "__orig_bases__"):
        for subclass in c.__orig_bases__:
            subclass_generic = generic_of(subclass, t, subclass=True)
            if subclass_generic is not None:
                return subclass_generic
    if not subclass:
        raise TypeError("Superclass does not inherit BaseClient")
    return None
