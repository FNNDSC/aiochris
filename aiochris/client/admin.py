import io
import json
from typing import Iterable

import aiohttp
from async_property import async_cached_property
from serde import from_dict

from aiochris.client.authed import AuthenticatedClient
from aiochris.link import http
from aiochris.link.collection_client import CollectionJsonApiClient
from aiochris.link.linked import deserialize_linked
from aiochris.models.collection_links import (
    AdminCollectionLinks,
    AdminApiCollectionLinks,
)
from aiochris.models.logged_in import Plugin
from aiochris.models.public import ComputeResource
from aiochris.types import PluginUrl, ComputeResourceName, PfconUrl
from aiochris.errors import raise_for_status


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

    async def add_plugin(
        self,
        plugin_description: str | dict,
        compute_resources: str
        | ComputeResource
        | Iterable[ComputeResource | ComputeResourceName],
    ) -> Plugin:
        """
        Add a plugin to *CUBE*.

        Examples
        --------

        ```python
        cmd = ['docker', 'run', '--rm', 'fnndsc/pl-mri-preview', 'chris_plugin_info']
        output = subprocess.check_output(cmd, text=True)
        desc = json.loads(output)
        desc['name'] = 'pl-mri-preview'
        desc['public_repo'] = 'https://github.com/FNNDSC/pl-mri-preview'
        desc['dock_image'] = 'fnndsc/pl-mri-preview'

        await chris_admin.add_plugin(plugin_description=desc, compute_resources='host')
        ```

        The example above is just for show. It's not a good example for several reasons:

        - Calls blocking function `subprocess.check_output` in asynchronous context
        - It is preferred to use a versioned string for `dock_image`
        - `host` compute environment is not guaranteed to exist. Instead, you could
          call `aiochris.client.authed.AuthenticatedClient.search_compute_resources`
          or `aiochris.client.authed.AuthenticatedClient.get_all_compute_resources`:

        ```python
        all_computes = await chris_admin.get_all_compute_resources()
        await chris_admin.add_plugin(plugin_description=desc, compute_resources=all_computes)
        ```

        Parameters
        ----------
        plugin_description: str | dict
            JSON description of a plugin.
            [spec](https://github.com/FNNDSC/CHRIS_docs/blob/5078aaf934bdbe313e85367f88aff7c14730a1d4/specs/ChRIS_Plugins.adoc#descriptor_file)
        compute_resources
            Compute resources to register the plugin to. Value can be either a comma-separated `str` of names,
            a `aiochris.models.public.ComputeResource`, a sequence of `aiochris.models.public.ComputeResource`,
            or a sequence of compute resource names as `str`.
        """
        compute_names = _serialize_crs(compute_resources)
        if not isinstance(plugin_description, str):
            plugin_description = json.dumps(plugin_description)
        data = aiohttp.FormData()
        data.add_field(
            "fname",
            io.StringIO(plugin_description),
            filename="aiochris_add_plugin.json",
        )
        data.add_field("compute_names", compute_names)
        async with self.s.post(self.collection_links.admin, data=data) as res:
            await raise_for_status(res)
            return deserialize_linked(self, Plugin, await res.json())

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


def _serialize_crs(
    c: str | ComputeResource | Iterable[ComputeResource | ComputeResourceName],
) -> str:
    if isinstance(c, str):
        return c
    if isinstance(c, ComputeResource):
        return c.name
    if not isinstance(c, Iterable):
        raise TypeError("compute_resources must be str or Iterable")
    return ",".join(map(_serialize_cr, c))


def _serialize_cr(c: str | ComputeResource):
    if isinstance(c, ComputeResource):
        return c.name
    return str(c)
