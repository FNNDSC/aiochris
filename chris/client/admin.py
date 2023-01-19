from typing import Iterable

from async_property import async_cached_property
from serde import from_dict

from chris.client.authed import AuthenticatedClient
from chris.link import http
from chris.link.collection_client import CollectionJsonApiClient
from chris.models.collection_links import AdminCollectionLinks, AdminApiCollectionLinks
from chris.models.logged_in import Plugin
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
        name: str | ComputeResourceName,
        compute_url: str | PfconUrl,
        compute_user: str,
        compute_password: str,
        description: str = None,
        compute_auth_url: str = None,
        compute_auth_token: str = None,
        max_job_exec_seconds: str = None,
    ) -> ComputeResource:
        """
        Define a new compute resource.
        """
        return await (await self._admin).create_compute_resource(
            name=name,
            compute_url=compute_url,
            compute_user=compute_user,
            compute_password=compute_password,
            description=description,
            compute_auth_url=compute_auth_url,
            compute_auth_token=compute_auth_token,
            max_job_exec_seconds=max_job_exec_seconds,
        )

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
