import abc
import dataclasses
from typing import (
    Final,
    Any,
    Optional,
    Callable,
    Type,
    TypeGuard,
    TypeVar,
    AsyncContextManager,
)

import aiohttp
import serde
import yarl
import importlib

from aiochris.errors import raise_for_status, StatusError

T = TypeVar("T")


class LinkedMeta(abc.ABCMeta):
    """
    A metaclass for HTTP clients which make requests to URIs
    that come from the API.
    """

    __DECORATED_METHOD_MARK: Final = "_link_name"
    """
    An attribute name which is set on functions decorated by the
    method decorators in this module.
    """

    def __new__(mcs, name, bases, dct):
        c = super().__new__(mcs, name, bases, dct)
        if abc.ABC in bases:
            return c

        if not mcs._is_linked(c):
            raise TypeError(f"{c} must be a subclass of {Linked}")

        mcs._validate_collection_names(c, dct)
        return c

    @classmethod
    def _is_linked(cls, c) -> TypeGuard[Type["Linked"]]:
        return issubclass(c, Linked)

    @classmethod
    def _validate_collection_names(mcs, cls: Type["Linked"], dct: dict[str, Any]):
        """
        Check that every method marked by `mark_to_check` was given a collection name
        which exists as a field in the class's associated
        `aiochris.models.collection_links.AbstractCollectionLinks` type.
        """
        marked_methods = filter(None, map(mcs._get_marked, dct.values()))
        for collection_name, method in marked_methods:
            if not cls._has_link(collection_name):
                raise TypeError(
                    f'Method {method} needs link "{collection_name}" '
                    f"but {cls} does not have it"
                )

    @classmethod
    def _get_marked(mcs, method: Any) -> Optional[tuple[str, Callable]]:
        if not callable(method):
            return None
        if hasattr(method, mcs.__DECORATED_METHOD_MARK):
            link_name = getattr(method, mcs.__DECORATED_METHOD_MARK)
            return link_name, method
        return None

    @classmethod
    def mark_to_check(mcs, method: Callable, link_name: str) -> None:
        """
        Indicate that the given method has a data dependency on a link.
        """
        if not callable(method):
            raise TypeError("method must be callable")
        setattr(method, mcs.__DECORATED_METHOD_MARK, link_name)


_S = TypeVar("_S")


def _deserialize_noop_hack(s: _S) -> _S:
    setattr(s, "_AIOCHRIS_LINKED_DESERIALIZED", True)
    return s


def _skip_hacked(s: any) -> bool:
    if getattr(s, "_AIOCHRIS_LINKED_DESERIALIZED"):
        return False
    return True


@serde.serde
@dataclasses.dataclass(frozen=True)
class Linked(abc.ABC, metaclass=LinkedMeta):
    """
    A `Linked` is an object which can make HTTP requests to links from an API.
    """

    # The functions `_deserialize_noop_hack` and `_skip_hacked`  are used with `serde.field`
    # so that `s` is included in deserialization, but excluded when serialized.
    s: aiohttp.ClientSession = serde.field(
        deserializer=_deserialize_noop_hack,
        serializer=lambda s: s,
        skip_if=_skip_hacked,
    )

    max_search_requests: int
    """
    Maximum number of requests to make for pagination.
    """

    @classmethod
    @abc.abstractmethod
    def _has_link(cls, name: str) -> bool: ...

    @abc.abstractmethod
    def _get_link(self, name: str) -> yarl.URL: ...


@serde.serde
@dataclasses.dataclass(frozen=True)
class LinkedModel(Linked, abc.ABC):
    """
    A class where its fields may be API links.
    """

    def to_dict(self) -> dict:
        """Serialize this object."""
        return serde.to_dict(self)

    @classmethod
    def _has_link(cls, name: str) -> bool:
        return any(name == field for field in cls._field_names())

    @classmethod
    def _field_names(cls) -> frozenset[str]:
        # LinkedMeta.__new__ is called before the dataclasses.dataclass
        # decorator, so dataclasses.fields only returns the superclass fields.
        # Hence, it is necessary to also check __annotations__
        return frozenset(
            (*(f.name for f in dataclasses.fields(cls)), *cls.__annotations__.keys())
        )

    def _get_link(self, name: str) -> yarl.URL:
        return yarl.URL(getattr(self, name))


def deserialize_linked(client: Linked, t: Type[T], o: dict) -> T:
    """
    Wraps `serde.from_dict`.
    If `t` is a dataclass with a field `s: aiohttp.ClientSession`, its session is set.

    Side effect: o is mutated
    """
    fixed_t = _beartype_workaround410(t)
    if _needs_session_field(fixed_t):
        o["s"] = client.s
        o["max_search_requests"] = client.max_search_requests
    return serde.from_dict(fixed_t, o, reuse_instances=True)


async def deserialize_res(
    sent_request: AsyncContextManager[aiohttp.ClientResponse],
    client: Linked,
    sent_data: dict,
    return_type: Type[T],
) -> T:
    async with sent_request as res:
        try:
            await raise_for_status(res)
        except StatusError as e:
            e.request_data = sent_data
            raise e
        if return_type is type(None):  # noqa
            return None
        sent_data = await res.json(content_type="application/json")
    return deserialize_linked(client, return_type, sent_data)


def _needs_session_field(t) -> bool:
    """
    Check whether `t` is a dataclass which has a field `s` with type `aiohttp.ClientSession`.
    """
    if not dataclasses.is_dataclass(t):
        return False
    return next(filter(_is_s_session_field, dataclasses.fields(t)), None) is not None


def _is_s_session_field(s: dataclasses.Field) -> bool:
    return s.name == "s" and s.type is aiohttp.ClientSession


def _beartype_workaround410(t):
    """
    See https://github.com/beartype/beartype/issues/410#issuecomment-2249195428
    """
    return getattr(t, "__type_beartype__", None) or t
