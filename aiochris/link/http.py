"""
Decorators for making HTTP requests to API links.

The specified URLs for API endpoints come from the API itself,
so URLs are resolved at the time a method is called.

The decorated method's `**kwargs` are serialized and sent along with the HTTP request,
and the response is deserialized according to the method's return type hint.
"""

import functools
import logging
import typing
from typing import (
    Callable,
    TypeVar,
    Type,
    Any,
    Optional,
    AsyncContextManager,
    Coroutine,
)

import aiohttp
import yarl

from aiochris.link.linked import LinkedMeta, Linked, deserialize_res
from aiochris.link.metaprog import get_return_hint
from aiochris.util.search import Search

logger = logging.getLogger(__name__)

_R = TypeVar("_R")

# Some metaprogramming gotchas:
# The type annotations of a function given to a decorator might not exist
# at the time of the decorator's execution, in the case of "forward references"
# (which is where a type is specified as a str instead of a class/type).
# The return type and the type of `self` can only be checked inside the wrapped
# function and not in the decorator.


def get(link_name: str):
    """
    Creates a decorator for which replaces the given method with one that does a GET request.
    """
    return _http_method_decorator(
        link_name=link_name,
        method_name="GET",
        request=lambda session, url, query: session.get(url, params=query),
    )


def post(link_name: str):
    """
    Creates a decorator for which replaces the given method with one that does a POST request.
    """
    return _http_method_decorator(
        link_name=link_name,
        method_name="POST",
        request=lambda session, url, data: session.post(url, json=data),
    )


def put(link_name: str):
    """
    Creates a decorator for which replaces the given method with one that does a PUT request.
    """
    return _http_method_decorator(
        link_name=link_name,
        method_name="PUT",
        request=lambda session, url, data: session.put(url, json=data),
    )


def delete(link_name: str):
    """
    Creates a decorator for which replaces the given method with one that does a DELETE request.
    """
    return _http_method_decorator(
        link_name=link_name,
        method_name="DELETE",
        request=lambda session, url, _: session.delete(url),
    )


Request = Callable[
    [aiohttp.ClientSession, yarl.URL, dict[str, Any]],
    AsyncContextManager[aiohttp.ClientResponse],
]
"""
A function which does a HTTP request.
"""


def _http_method_decorator(
    link_name: str, method_name: str, request: Request
) -> Callable[
    [Callable[..., Coroutine[None, None, _R]]], Callable[..., Coroutine[None, None, _R]]
]:
    """
    Creates a decorator which transforms a method of a subclass of `aiochris.link.Linked`
    to one which makes an HTTP request.
    """

    def decorator(
        fn: Callable[..., Coroutine[None, None, _R]]
    ) -> Callable[..., Coroutine[None, None, _R]]:
        @functools.wraps(fn)
        async def wrapped(self: Linked, *args, **kwargs) -> _R:
            if args:
                raise TypeError(f"Function {fn} only supports kwargs.")
            return_type = get_return_hint(fn)
            url = self._get_link(link_name)
            data = _filter_none(kwargs)
            logger.debug(f"{method_name} --> {url} : {data}")
            sent = request(self.s, url, data)
            return await deserialize_res(sent, self, data, return_type)

        LinkedMeta.mark_to_check(wrapped, link_name)
        return wrapped

    return decorator


def search(
    collection_name: str, subpath: str = "search/"
) -> Callable[[Callable[..., Search[_R]]], Callable[..., Search[_R]]]:
    """
    Creates a decorator which searches the collection using GET requests.

    (Pagination is handled internally, HTTP requests are made as-needed.)
    """

    def decorator(fn: Callable[..., Search[_R]]) -> Callable[..., Search[_R]]:
        @functools.wraps(fn)
        def wrapped(self: Linked, *args, **kwargs) -> Search[_R]:
            if args:
                raise TypeError(f"Function {fn} only supports kwargs.")
            return_item_type = _get_search_item_type(fn)

            return Search[return_item_type](
                Item=return_item_type,
                client=self,
                base_url=self._get_link(collection_name),
                params=kwargs,
                max_requests=self.max_search_requests,
                subpath=subpath,
            )

        LinkedMeta.mark_to_check(wrapped, collection_name)
        return wrapped

    return decorator


def _get_search_item_type(fn: Callable[..., Search[_R]]) -> Type[_R]:
    return_type = get_return_hint(fn)
    if typing.get_origin(return_type) is not Search:
        raise TypeError(return_type)
    return typing.get_args(return_type)[0]


K = TypeVar("K")
V = TypeVar("V")


def _filter_none(d: dict[K, Optional[V]]) -> dict[K, V]:
    return {k: v for k, v, in d.items() if v is not None}
