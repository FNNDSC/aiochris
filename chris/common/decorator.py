import functools
import logging
import urllib.parse
from typing import Callable, Type, TypeVar, get_type_hints

from serde.json import from_json

from chris.base import AbstractClient
from chris.helper.errors import raise_for_status, ResponseError
from chris.models.types import ChrisURL

logger = logging.getLogger(__name__)
_R = TypeVar("_R")


def post(endpoint: str):
    """
    Creates a decorator for methods of an `AbstractClient` which replaces
    the given method with one that does a POST request using its given `**kwargs`,
    then deserializes the response according to the method's return type hint,
    and returns that result.
    """

    def decorator(fn: Callable[[...], _R]):
        return_type = _get_return_hint(fn)

        @functools.wraps(fn)
        async def wrapped(self: AbstractClient, *_, **kwargs: str) -> _R:
            if _:
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


def _join_endpoint(url: ChrisURL, endpoint: str) -> str:
    if endpoint.startswith("/"):
        return urllib.parse.urlparse(url)._replace(path=endpoint).geturl()
    return url + endpoint


def _get_return_hint(fn: Callable[[...], _R]) -> Type[_R]:
    hints = get_type_hints(fn)
    if "return" not in hints:
        raise ValueError(f"Function {fn} must define a return type hint.")
    return hints["return"]
