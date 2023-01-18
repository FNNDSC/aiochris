import dataclasses
from typing import TypeVar, Generic, Type

import yarl

from chris.link.linked import Linked
from chris.link.metaprog import generic_of
from chris.models.collection_links import AbstractCollectionLinks

L = TypeVar("L", bound=AbstractCollectionLinks)


@dataclasses.dataclass(frozen=True)
class CollectionJsonApiClient(Generic[L], Linked):
    """
    A class base for HTTP clients which accept "application/json" from a Collection+JSON API.
    """

    collection_links: L

    def _get_link(self, name: str) -> yarl.URL:
        link = self.collection_links.get(name)
        return yarl.URL(link)

    @classmethod
    def _has_link(cls, name: str) -> bool:
        return cls._collection_type().has_field(name)

    @classmethod
    def _collection_type(cls) -> Type[L]:
        return generic_of(cls, AbstractCollectionLinks)
