import abc
from dataclasses import dataclass
from typing import TypeVar, Generic

import aiohttp

from chris.client.meta import CollectionClientMeta
from chris.models.collection_links import AbstractCollectionLinks

# in Python 3.11 we will be able to use Self!
CSelf = TypeVar("CSelf", bound="AbstractChrisClient")

_C = TypeVar("_C", bound="AuthenticatedClient")
L = TypeVar("L", bound=AbstractCollectionLinks)


@dataclass(frozen=True)
class AbstractClient(
    Generic[L],
    abc.ABC,
    metaclass=CollectionClientMeta,
):
    """
    Class which specifies the fields which a ChRIS API related client must have.
    """

    collection_links: L
    s: aiohttp.ClientSession
    url: str
    max_requests: int = 1000
    """
    Maximum number of requests to make for pagination.
    """

    @classmethod
    def has_collection(cls, name: str) -> bool:
        """
        Parameters
        ----------
        name
            name from collection_links

        Returns
        -------
        `True` if this class' `collection_links` has a link for the name
        """
        return cls.collection_links_type.has_field(name)
