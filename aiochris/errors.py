import aiohttp


async def raise_for_status(res: aiohttp.ClientResponse) -> None:
    """
    Raises custom exceptions.
    """
    if res.status < 400:
        res.raise_for_status()
        return
    exception = BadRequestError if res.status < 500 else InternalServerError
    try:
        raise exception(res.status, res.url, await res.json())
    except aiohttp.ClientError:
        raise exception(res.status, res.url)


class BaseClientError(Exception):
    pass


class ResponseError(BaseClientError):
    pass


class BadRequestError(ResponseError):
    pass


class InternalServerError(ResponseError):
    pass


class IncorrectLoginError(BaseClientError):
    pass


class NonsenseResponseError(ResponseError):
    """CUBE returned data which does not make sense."""

    pass
