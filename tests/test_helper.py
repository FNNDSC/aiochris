from chris import ChrisClient, AnonChrisClient
from chris.client.base import generic_of
from chris.models.collection_links import AnonymousCollectionLinks, CollectionLinks


def test_generic_of():
    assert (
        generic_of(AnonChrisClient, AnonymousCollectionLinks)
        is AnonymousCollectionLinks
    )
    assert generic_of(ChrisClient, AnonymousCollectionLinks) is CollectionLinks
