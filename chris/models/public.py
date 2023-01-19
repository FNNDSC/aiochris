"""
Read-only models for CUBE resources.
"""
from dataclasses import dataclass

from serde import deserialize

from chris.link.linked import LinkedModel
from chris.models.types import *


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
