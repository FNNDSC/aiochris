import asyncio
from dataclasses import dataclass

import pytest
import aiohttp
from aiochris.models.types import ChrisURL, Username, Password


@pytest.fixture(scope="session")
def event_loop():
    """
    https://stackoverflow.com/questions/56236637/using-pytest-fixturescope-module-with-pytest-mark-asyncio/56238383#56238383
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def session(event_loop: asyncio.AbstractEventLoop) -> aiohttp.ClientSession:
    async with aiohttp.ClientSession(loop=event_loop) as session:
        yield session


@dataclass
class UserCredentials:
    username: Username
    password: Password
    url: ChrisURL


@pytest.fixture(scope="session")
def admin_credentials() -> UserCredentials:
    return UserCredentials(
        username=Username("chris"),
        password=Password("chris1234"),
        url=ChrisURL("http://localhost:8000/api/v1/"),
    )
