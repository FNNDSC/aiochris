from typing import Iterable, Sequence

from async_property import async_cached_property
from serde import from_dict

from chris.client.authed import AuthenticatedClient
from chris.link.collection_client import CollectionJsonApiClient
from chris.link import http
from chris.models.logged_in import Plugin

from chris.util.search import acollect
from chris.models.collection_links import AdminCollectionLinks, AdminApiCollectionLinks
from chris.models.public import ComputeResource
from chris.models.types import PluginUrl, ComputeResourceName, PfconUrl


class _AdminApiClient(CollectionJsonApiClient[AdminApiCollectionLinks]):
    """
    A client to `/chris-admin/api/v1/`
    """

    @http.post("compute_resources")
    async def create_compute_resource(self, **kwargs) -> ComputeResource:
        ...


class ChrisAdminClient(AuthenticatedClient[AdminCollectionLinks, "ChrisAdminClient"]):
    """
    A client who has access to `/chris-admin/`. Admins can register new plugins and
    add new compute resources.
    """

    @http.post("admin")
    async def _register_plugin_from_store_raw(
        self, plugin_store_url: str, compute_names: str
    ) -> Plugin:
        ...

    async def register_plugin_from_store(
        self, plugin_store_url: PluginUrl, compute_names: Iterable[ComputeResourceName]
    ) -> Plugin:
        """
        Register a plugin from a ChRIS Store.
        """
        return await self._register_plugin_from_store_raw(
            plugin_store_url=plugin_store_url, compute_names=",".join(compute_names)
        )

    async def create_compute_resource(
        self,
        name: ComputeResourceName,
        compute_url: PfconUrl,
        compute_user: str,
        compute_password: str,
        description: str = "",
    ) -> ComputeResource:
        """
        Define a new compute resource.
        """
        return await self._admin.create_compute_resource(
            name=name,
            compute_url=compute_url,
            compute_user=compute_user,
            compute_password=compute_password,
            description=description,
        )

    async def get_all_compute_resources(self) -> Sequence[ComputeResource]:
        return await acollect(self.search_compute_resources())

    @async_cached_property
    async def _admin(self) -> _AdminApiClient:
        """
        Get a (sub-)client for `/chris-admin/api/v1/`
        """
        res = await self.s.get(self.collection_links.admin)
        body = await res.json()
        links = from_dict(AdminApiCollectionLinks, body["collection_links"])
        return _AdminApiClient(
            url=self.collection_links.admin,
            s=self.s,
            collection_links=links,
            max_search_requests=self.max_search_requests,
        )
