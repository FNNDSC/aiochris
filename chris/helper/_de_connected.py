from typing import TypeVar, Type

import aiohttp
from serde import from_dict

from chris.models.connected import Connected

T = TypeVar("T")


def deserialize_connected(s: aiohttp.ClientSession, t: Type[T], o: dict) -> T:
    """
    Wraps `serde.from_dict`.
    If `t` is a subclass of `chris.models.connected.Connected`, its session is set.

    Side effect: o is mutated
    """
    if issubclass(t, Connected):
        o["s"] = s
    return from_dict(t, o, reuse_instances=True)
