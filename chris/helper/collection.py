import dataclasses
import functools
import logging
from typing import Callable, TypeVar

from serde.json import from_json

from chris.client.meta import CollectionClientMeta
from chris.client.base import AbstractChrisClient
from chris.helper.errors import raise_for_status, ResponseError
from chris.helper.metaprog import get_return_hint

logger = logging.getLogger(__name__)

_R = TypeVar("_R")


def post(collection_name: str):
    """
    Creates a decorator for methods of an `AbstractChrisClient` which replaces
    the given method with one that does a POST request using its given `**kwargs`,
    then deserializes the response according to the method's return type hint,
    and returns that result.

    The URL is retrieved from `self.collection_links`. Whether the specified value
    for `collection_name` is defined gets checked at class definition time by
    `chris.client.meta.CollectionClientMeta`.
    """

    def decorator(fn: Callable[[...], _R]):
        return_type = get_return_hint(fn)

        @functools.wraps(fn)
        async def wrapped(self: AbstractChrisClient, *args, **kwargs: str) -> _R:
            if args:
                raise TypeError(f"Function {fn} only supports kwargs.")

            url = self.collection_links.get(collection_name)
            logger.debug("POST --> {} : {}", url, kwargs)
            res = await self.s.post(url, json=kwargs, raise_for_status=False)
            try:
                await raise_for_status(res)
            except ResponseError as e:
                raise e.__class__(*e.args, f"data={kwargs}")
            return from_json(return_type, await res.text())

        CollectionClientMeta.mark_to_check(wrapped, collection_name)
        return wrapped

    return decorator
