from typing import Optional, Any

import aiohttp
import yarl


async def raise_for_status(res: aiohttp.ClientResponse) -> None:
    """
    Raises custom exceptions.
    """
    if res.status < 400:
        res.raise_for_status()
        return
    if res.status == 401:
        raise UnauthorizedError()
    exception = BadRequestError if res.status < 500 else InternalServerError
    try:
        raise exception(res.status, res.url, await res.json())
    except aiohttp.ClientError:
        raise exception(res.status, res.url)


class BaseClientError(Exception):
    """Base error raised by aiochris functions."""

    pass


class StatusError(BaseClientError):
    """Base exception for 4xx and 5xx HTTP codes."""

    def __init__(
        self,
        status: int,
        url: yarl.URL,
        message: Optional[Any] = None,
        request_data: Optional[Any] = None,
    ):
        super().__init__()
        self.status = status
        """HTTP status code"""
        self.url = url
        """URL where this error comes from"""
        self.message = message
        """Response body"""
        self.request_data = request_data
        """Request body"""


class BadRequestError(StatusError):
    """Bad request error."""

    pass


class InternalServerError(StatusError):
    """Internal server error."""

    pass


class UnauthorizedError(BaseClientError):
    """Unauthorized request."""

    pass


class IncorrectLoginError(BaseClientError):
    """Failed HTTP basic auth with bad username or password."""

    pass


class NonsenseResponseError(BaseClientError):
    """CUBE returned data which does not make sense."""

    pass
