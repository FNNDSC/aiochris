import abc
from pathlib import Path
from chris.common.models import Plugin
from chris.store.models import AnonymousCollectionLinks, StoreCollectionLinks
import aiohttp
from serde.json import from_json
from typing import TypeVar
from chris.common.client import AbstractClient, AnonymousClient, AuthenticatedClient
from chris.common.errors import raise_for_status


_L = TypeVar("_L", bound=AnonymousCollectionLinks)


class AbstractChrisStoreClient(AbstractClient[_L, Plugin], abc.ABC):
    pass


class AnonymousChrisStoreClient(
    AnonymousClient[AnonymousCollectionLinks, Plugin, "AnonymousChrisStoreClient"],
    AbstractChrisStoreClient[AnonymousCollectionLinks],
):
    """
    An unauthenticated *ChRIS Store* client.
    """
    pass


class ChrisStoreClient(
    AuthenticatedClient[StoreCollectionLinks, Plugin, "ChrisStoreClient"],
    AbstractChrisStoreClient[StoreCollectionLinks],
):
    """
    An authenticated *ChRIS Store* client.
    """
    async def upload_plugin(
        self, name: str, dock_image: str, public_repo: str, descriptor_file: Path
    ) -> Plugin:
        """
        Upload a plugin representation file to this *ChRIS Store*.
        """
        form = aiohttp.FormData()
        form.add_field("name", name)
        form.add_field("dock_image", dock_image)
        form.add_field("public_repo", public_repo)

        with descriptor_file.open("rb") as open_file:
            form.add_field(
                "descriptor_file",
                open_file,
                filename=descriptor_file.name,
                content_type="application/json",
            )
            res = await self.s.post(
                self.collection_links.plugins, data=form, raise_for_status=False
            )
        await raise_for_status(res)
        return from_json(Plugin, await res.text())
