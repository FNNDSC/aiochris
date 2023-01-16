import aiohttp


async def raise_for_status(res: aiohttp.ClientResponse) -> None:
    """
    Raises custom exceptions.
    """
    if res.status < 400:
        res.raise_for_status()
        return
    exception = BadRequestError if res.status < 500 else InternalServerError
    raise exception(res.status, res.url, await res.json())


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


class DeserializationError(BaseClientError):
    pass


class EmptySearchError(BaseClientError):
    pass


class PluralResultsError(BaseClientError):
    pass
