import asyncio
import pytest
import aiohttp
from typing import TypedDict
from chris.common.types import ChrisURL, ChrisUsername, ChrisPassword


@pytest.fixture(scope="session")
def event_loop():
    """
    https://stackoverflow.com/questions/56236637/using-pytest-fixturescope-module-with-pytest-mark-asyncio/56238383#56238383
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def session(event_loop) -> aiohttp.ClientSession:
    async with aiohttp.ClientSession(loop=event_loop) as session:
        yield session


@pytest.fixture(scope="session")
def cube_url():
    return ChrisURL("http://localhost:8000/api/v1/")


class UserCredentials(TypedDict):
    username: ChrisUsername
    password: ChrisPassword


@pytest.fixture(scope="session")
def cube_superuser() -> UserCredentials:
    return {"username": ChrisUsername("chris"), "password": ChrisPassword("chris1234")}
