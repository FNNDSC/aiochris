"""
Read-only models for CUBE resources.
"""
from dataclasses import dataclass

import serde
from serde import deserialize

from aiochris.link import http
from aiochris.link.linked import LinkedModel
from aiochris.models.enums import PluginType
from aiochris.models.types import *
from aiochris.util.search import Search


@deserialize
@dataclass(frozen=True)
class ComputeResource:
    url: ApiUrl
    id: ComputeResourceId
    creation_date: str
    modification_date: str
    name: ComputeResourceName
    compute_url: PfconUrl
    compute_auth_url: str
    description: str
    max_job_exec_seconds: int


@deserialize
@dataclass(frozen=True)
class PublicPlugin(LinkedModel):
    """
    A ChRIS plugin.
    """

    url: PluginUrl
    id: PluginId
    name: PluginName
    version: PluginVersion
    dock_image: ImageTag
    public_repo: str
    compute_resources: ComputeResourceUrl
    plugin_type: PluginType = serde.field(rename="type")

    @http.get("compute_resources")
    def get_compute_resources(self) -> Search[ComputeResource]:
        """Get the compute resources this plugin is registered to."""
        ...
