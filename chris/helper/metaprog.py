"""
Metaprogramming helper functions.
"""
import sys
import typing
from typing import Type, Callable, TypeVar, ForwardRef, Optional
import typing_inspect

_T = TypeVar("_T")


def get_return_hint(fn: Callable[[...], _T]) -> Type[_T]:
    hints = typing.get_type_hints(fn)
    if "return" not in hints:
        raise ValueError(f"Function {fn} must define a return type hint.")
    return hints["return"]


def get_class_of_method(method: Callable) -> Type:
    split = method.__qualname__.split(".")
    if len(split) != 2:
        raise ValueError(f"{method} does not look like a method")
    class_name, _method_name = split
    module = method.__module__  # noqa
    return vars(sys.modules[module])[class_name]


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
        raise ValueError("Superclass does not inherit BaseClient")
    return None
