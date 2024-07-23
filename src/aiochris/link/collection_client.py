import dataclasses
from typing import TypeVar, Generic, Type

import yarl

from aiochris.link.linked import Linked
from aiochris.link.metaprog import generic_of
from aiochris.models.collection_links import AbstractCollectionLinks

L = TypeVar("L", bound=AbstractCollectionLinks)


@dataclasses.dataclass(frozen=True)
class CollectionJsonApiClient(Generic[L], Linked):
    """
    A class base for HTTP clients which accept "application/json" from a Collection+JSON API.

    The special value "." is recognized as a way to refer to the collection of the base URL.
    For *CUBE*, it would get the feeds.
    """

    url: str
    """Base API URL"""
    collection_links: L
    """Base API collection links"""

    def _get_link(self, name: str) -> yarl.URL:
        if name == ".":
            return yarl.URL(self.url)
        link = self.collection_links.get(name)
        return yarl.URL(link)

    @classmethod
    def _has_link(cls, name: str) -> bool:
        return name == "." or cls._collection_type().has_field(name)

    @classmethod
    def _collection_type(cls) -> Type[L]:
        return generic_of(cls, AbstractCollectionLinks)
