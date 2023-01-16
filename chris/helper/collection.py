import functools
import logging
import urllib.parse
import dataclasses
from typing import Callable, Type, TypeVar, TypeGuard

from serde.json import from_json

from chris.client.base import AbstractChrisClient
from chris.helper.errors import raise_for_status, ResponseError
from chris.helper.metaprog import get_class_of_method, get_return_hint, generic_of
from chris.models.collection_links import AnonymousCollectionLinks
from chris.models.types import ChrisURL, ApiUrl

logger = logging.getLogger(__name__)

_R = TypeVar("_R")


def post(collection_name: ApiUrl):
    """
    Creates a decorator for methods of an `AbstractChrisClient` which replaces
    the given method with one that does a POST request using its given `**kwargs`,
    then deserializes the response according to the method's return type hint,
    and returns that result.

    The URL is retrieved from `self.collection_links`.
    """

    def decorator(fn: Callable[[...], _R]):
        cls = get_class_of_method(fn)
        return_type = get_return_hint(fn)
        if not is_chris_client_class(cls):
            raise ValueError(
                f"The class of given method {fn} is not a subclass of AbstractChrisClient"
            )

        @functools.wraps(fn)
        async def wrapped(self: AbstractChrisClient, *args, **kwargs: str) -> _R:
            if args:
                raise TypeError(f"Function {fn} only supports kwargs.")

            url = _join_endpoint(self.url, endpoint)
            logger.debug("POST --> {} : {}", url, kwargs)
            res = await self.s.post(url, json=kwargs, raise_for_status=False)
            try:
                await raise_for_status(res)
            except ResponseError as e:
                raise e.__class__(*e.args, f"data={kwargs}")
            return from_json(return_type, await res.text())

        return wrapped

    return decorator


def join_endpoint(url: ChrisURL, endpoint: str) -> str:
    if endpoint.startswith("/"):
        return urllib.parse.urlparse(url)._replace(path=endpoint).geturl()
    return url + endpoint


def is_chris_client_class(cls: Type) -> TypeGuard[Type[AbstractChrisClient]]:
    return issubclass(cls, AbstractChrisClient)


def has_collection(cls: Type[AbstractChrisClient], collection_name: str) -> bool:
    fields = dataclasses.fields(cls.collection_links_type)
    return collection_name in (f.name for f in fields)
