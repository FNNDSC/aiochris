from typing import Optional, TypeVar, AsyncGenerator, Type, AsyncIterable, Any

import aiohttp
from serde import deserialize, from_dict
from serde.json import from_json

import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


@deserialize
class _Paginated:
    """
    Response from a paginated endpoint.
    """

    count: int
    next: Optional[str]
    previous: Optional[str]
    results: list[Any]


async def get_paginated(
    session: aiohttp.ClientSession,
    url: str,
    element_type: Type[T],
    max_requests: int = 100,
) -> AsyncGenerator[T, None]:
    """
    Make HTTP GET requests to a paginated endpoint. Further requests to the
    "next" URL are made in the background as needed.
    """
    logger.debug("GET, max_requests=%d, --> %s", max_requests, url)
    if max_requests <= 0:
        raise TooMuchPaginationException()
    res = await session.get(url)
    data: _Paginated = from_json(_Paginated, await res.text())
    for element in data.results:
        yield from_dict(element_type, element)
    if data.next is not None:
        next_results = get_paginated(session, data.next, element_type, max_requests - 1)
        async for next_element in next_results:
            yield next_element


async def acollect(async_iterable: AsyncIterable[T]) -> list[T]:
    # nb: using tuple here causes
    #     TypeError: 'async_generator' object is not iterable
    # return tuple(e async for e in async_iterable)
    return [e async for e in async_iterable]


class TooMuchPaginationException(Exception):
    pass
