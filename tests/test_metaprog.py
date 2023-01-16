"""
Testing metaprogramming without using any of the public classes of this package
nor any real HTTP requests.
"""

from dataclasses import dataclass

import aiohttp
import pytest
from pytest_mock import MockerFixture

from chris.client.base import AbstractClient
from chris.helper.metaprog import get_return_hint
from chris.models.collection_links import AbstractCollectionLinks

from chris.models.types import ApiUrl
from chris.helper import collection


@dataclass(frozen=True)
class ExampleCollectionLinks(AbstractCollectionLinks):
    example_collection_name: ApiUrl


class ExampleClient(AbstractClient[ExampleCollectionLinks]):
    @collection.post("example_collection_name")
    async def example_method(self, a_param: str) -> list:
        ...


def test_get_return_hint():
    assert get_return_hint(ExampleClient.example_method) is list


async def test_request_to_collection_link(mocker: MockerFixture):
    link = ApiUrl("https://example.com/post_to_link")
    links = ExampleCollectionLinks(example_collection_name=link)
    client = ExampleClient(
        url="https://example.com",
        collection_links=links,
        s=mocker.MagicMock(spec_set=aiohttp.ClientSession),
    )
    mock_response = mocker.AsyncMock()
    mock_response.raise_for_status = mocker.MagicMock()
    mock_response.status = 200
    mock_response.text = mocker.AsyncMock(return_value="[3, 4, 5]")
    client.s.post = mocker.AsyncMock(return_value=mock_response)

    res = await client.example_method(a_param="hello")
    assert res == [3, 4, 5]
    client.s.post.assert_called_once_with(
        link, json={"a_param": "hello"}, raise_for_status=mocker.ANY
    )


def test_metaclass_validates_links():
    expected_msg = (
        r"Method .+BadClient.bad_method.+ requests collection_link "
        r"\"a_name_that_dne\" which is not defined in .+ExampleCollectionLinks.*"
    )
    with pytest.raises(TypeError, match=expected_msg) as e:

        class BadClient(AbstractClient[ExampleCollectionLinks]):
            @collection.post("a_name_that_dne")
            async def bad_method(self, a_param: str) -> list:
                ...

    print(e.value.args)
