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
from typing import Callable, TypeVar, Type

from chris.util.errors import raise_for_status, ResponseError
from chris.link.metaprog import get_return_hint
from chris.util.search import Search
from chris.link.linked import LinkedMeta, Linked, deserialize_linked

logger = logging.getLogger(__name__)

_R = TypeVar("_R")


def post(link_name: str):
    """
    Creates a decorator for which replaces the given method with one that does a POST request.
    """

    def decorator(fn: Callable[[...], _R]):
        return_type = get_return_hint(fn)

        @functools.wraps(fn)
        async def wrapped(self: Linked, *args, **kwargs: str) -> _R:
            if args:
                raise TypeError(f"Function {fn} only supports kwargs.")

            url = self._get_link(link_name)
            logger.debug("POST --> {} : {}", url, kwargs)
            async with self.s.post(url, json=kwargs, raise_for_status=False) as res:
                try:
                    await raise_for_status(res)
                except ResponseError as e:
                    raise e.__class__(*e.args, f"data={kwargs}")
                data = await res.json(content_type="application/json")
            return deserialize_linked(self, return_type, data)

        LinkedMeta.mark_to_check(wrapped, link_name)
        return wrapped

    return decorator


def search(collection_name: str):
    """
    Creates a decorator which searches the collection using GET requests.

    (Pagination is handled internally, HTTP requests are made as-needed.)
    """

    def decorator(fn: Callable[[...], Search[_R]]):
        return_item_type = _get_search_item_type(fn)

        @functools.wraps(fn)
        def wrapped(self: Linked, *args, **kwargs: str) -> _R:
            if args:
                raise TypeError(f"Function {fn} only supports kwargs.")

            return Search[return_item_type](
                Item=return_item_type,
                client=self,
                base_url=self._get_link(collection_name),
                params=kwargs,
                max_requests=self.max_search_requests,
            )

        LinkedMeta.mark_to_check(wrapped, collection_name)
        return wrapped

    return decorator


def _get_search_item_type(fn: Callable[[...], Search[_R]]) -> Type[_R]:
    return_type = get_return_hint(fn)
    if typing.get_origin(return_type) is not Search:
        raise TypeError(return_type)
    return typing.get_args(return_type)[0]
