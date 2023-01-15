"""
These types are private because they represent analogous
features between _ChRIS_ store and _CUBE_, but are not
directly interoperable.
e.g. `https://chrisstore.co/api/v1/plugins/search`
and `https://cube.chrisproject.org/api/v1/plugins/search/`
are analogous but one wouldn't make sense in the context
of the other.
"""
from typing import NewType, Optional, TypeVar, AsyncGenerator, Type, AsyncIterable, Any

import aiohttp
from serde import deserialize, from_dict
from serde.json import from_json

import logging

logger = logging.getLogger(__name__)


PaginatedUrl = NewType("PaginatedUrl", str)
T = TypeVar("T")


@deserialize
class _Paginated:
    """
    Response from a paginated endpoint.
    """
    count: int
    next: Optional[PaginatedUrl]
    previous: Optional[PaginatedUrl]
    results: list[Any]


async def get_paginated(
    session: aiohttp.ClientSession,
    url: PaginatedUrl,
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


async def to_sequence(async_iterable: AsyncIterable[T]) -> list[T]:
    # nb: using tuple here causes
    #     TypeError: 'async_generator' object is not iterable
    # return tuple(e async for e in async_iterable)
    return [e async for e in async_iterable]


class TooMuchPaginationException(Exception):
    pass
