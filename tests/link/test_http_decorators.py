"""
Testing metaprogramming without using any of the public classes of this package
nor any real HTTP requests.
"""
import json
from dataclasses import dataclass
import dataclasses
from typing import AsyncContextManager, Any
from unittest.mock import Mock, AsyncMock

import yarl
import aiohttp
import pytest
from pytest_mock import MockerFixture

from chris.link.collection_client import CollectionJsonApiClient
from chris.link import http
from chris.util.search import Search
from chris.models.collection_links import AbstractCollectionLinks

from chris.models.types import ApiUrl


@dataclass(frozen=True)
class ExampleCollectionLinks(AbstractCollectionLinks):
    example_collection_name: ApiUrl
    another_name: ApiUrl


@dataclass(frozen=True)
class ExampleClient(CollectionJsonApiClient[ExampleCollectionLinks]):
    @http.post("example_collection_name")
    async def example_method(self, a_param: str) -> list:
        ...

    @http.search("another_name")
    def example_search(self, **kwargs) -> Search[str]:
        ...


@pytest.fixture
def example_client(mocker: MockerFixture) -> ExampleClient:
    link = ApiUrl("https://example.com/post_to_link")
    another_link = ApiUrl("https://example.com/something/")
    links = ExampleCollectionLinks(
        example_collection_name=link, another_name=another_link
    )
    return ExampleClient(
        collection_links=links,
        s=mocker.MagicMock(spec_set=aiohttp.ClientSession),
        max_search_requests=10,
        url="https://example.com/",
    )


@dataclass
class MockResponse:
    data: Any
    status: int = 200
    text: AsyncMock = dataclasses.field(default_factory=AsyncMock)
    json: AsyncMock = dataclasses.field(default_factory=AsyncMock)
    raise_for_status: Mock = dataclasses.field(default_factory=Mock)

    def __post_init__(self):
        self.text.return_value = json.dumps(self.data)
        self.json.return_value = self.data


class MockRequest(AsyncContextManager[Mock]):
    def __init__(self, data, status):
        super().__init__()
        self.res = MockResponse(data, status)

    async def __aenter__(self):
        return self.res

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @classmethod
    def using(cls, mocker: MockerFixture, data=None, status=200) -> Mock:
        return mocker.Mock(return_value=MockRequest(data, status))


async def test_mock_request(example_client: ExampleClient, mocker: MockerFixture):
    expected = ["apple", 345]
    url = "https://example.com/test_mock"
    example_client.s.post = MockRequest.using(mocker, expected)
    async with example_client.s.post(url) as res:
        assert isinstance(res, MockResponse)
        assert res.json.return_value == expected
        actual = await res.json()
        assert actual == expected
    example_client.s.post.assert_called_once_with(url)


async def test_request_to_collection_link(
    example_client: ExampleClient, mocker: MockerFixture
):
    example_client.s.post = MockRequest.using(mocker, [3, 4, 5])
    res = await example_client.example_method(a_param="hello")
    assert res == [3, 4, 5]
    example_client.s.post.assert_called_once_with(
        yarl.URL(example_client.collection_links.example_collection_name),
        json={"a_param": "hello"},
        raise_for_status=mocker.ANY,
    )


async def test_search(example_client: ExampleClient, mocker: MockerFixture):
    first_res = {
        "count": 5,
        "next": "https://example.com/something/search/?limit=3&offset=3",
        "previous": None,
        "results": ["yellowfin", "tuna", "salmon"],
    }
    example_client.s.get = MockRequest.using(mocker, first_res)
    search = example_client.example_search(animal="fish", edible="yes")
    assert search.Item is str
    example_client.s.get.assert_not_called()

    assert await search.count() == first_res["count"]
    example_client.s.get.assert_called_once()
    called_url: yarl.URL = example_client.s.get.call_args.args[0]
    assert "limit=1" in called_url.query_string
    assert "offset=0" in called_url.query_string
    assert called_url.query_string.count("limit") == 1
    assert called_url.query_string.count("offset") == 1
    example_client.s.get.reset_mock()

    search_iter = aiter(search)
    assert await anext(search_iter) == "yellowfin"
    expected_uri = "https://example.com/something/search/?animal=fish&edible=yes"
    example_client.s.get.assert_called_once_with(yarl.URL(expected_uri))
    example_client.s.get.reset_mock()

    assert await anext(search_iter) == "tuna"
    example_client.s.get.assert_not_called()
    assert await anext(search_iter) == "salmon"
    example_client.s.get.assert_not_called()

    second_res = {
        "count": 5,
        "next": None,
        "previous": "https://example.com/something/search/?animal=fish&edible=yes?limit=3&offset=0",
        "results": ["flounder", "swordfish"],
    }
    example_client.s.get = MockRequest.using(mocker, second_res)
    assert await anext(search_iter) == "flounder"
    example_client.s.get.assert_called_once_with(first_res["next"])
    example_client.s.get.reset_mock()
    assert await anext(search_iter) == "swordfish"
    assert await anext(search_iter, None) is None
    example_client.s.get.assert_not_called()
