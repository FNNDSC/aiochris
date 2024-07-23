from dataclasses import dataclass

import aiohttp
import pytest
from pytest_asyncio import is_async_test

from aiochris.types import ChrisURL, Username, Password

# N.B.: We're doing wacky things with asyncio, pytest, and aiohttp here.
# In our tests, notably in test_client.py, I want to use a session-scoped
# fixture to create a new CUBE user account. In order to do so, we need
# the definitions below for session and pytest_collection_modifyitems.


@pytest.fixture(scope="session")
async def session() -> aiohttp.ClientSession:
    async with aiohttp.ClientSession() as session:
        yield session


def pytest_collection_modifyitems(items):
    """
    See https://pytest-asyncio.readthedocs.io/en/latest/how-to-guides/run_session_tests_in_same_loop.html
    """
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)


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
