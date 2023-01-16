from typing import Iterable

from chris.client.authed import AuthenticatedClient
from chris.models.collection_links import AdminCollectionLinks, AdminApiCollectionLinks
from chris.helper import collection
from chris.models.res import Plugin
from chris.models.types import PluginUrl, ComputeResourceName
from chris.client.base import AbstractClient


class AdminApiClient(AbstractClient[AdminApiCollectionLinks]):
    """
    A client to `/chris-admin/api/v1/`
    """

    pass


class ChrisAdminClient(AuthenticatedClient[AdminCollectionLinks, "ChrisAdminClient"]):
    """
    A client who has access to `/chris-admin/`. Admins can register new plugins and
    add new compute resources.
    """

    @collection.post("admin")
    async def _register_plugin_from_store_raw(
        self, plugin_store_url: str, compute_names: str
    ) -> Plugin:
        ...

    async def register_plugin_from_store(
        self, plugin_store_url: PluginUrl, compute_names: Iterable[ComputeResourceName]
    ) -> Plugin:
        return await self._register_plugin_from_store_raw(
            plugin_store_url=plugin_store_url, compute_names=",".join(compute_names)
        )
