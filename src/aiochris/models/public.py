"""
Read-only models for CUBE resources.
"""
import sys
from dataclasses import dataclass
from typing import Optional, Literal, TextIO, Any

import serde
from serde import deserialize

from aiochris.link import http
from aiochris.link.linked import LinkedModel
from aiochris.enums import PluginType
from aiochris.types import *
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
class PluginParameter(LinkedModel):
    """
    Information about a parameter (a command-line option/flag) of a plugin.
    """

    url: PluginParameterUrl
    id: PluginParameterId
    name: ParameterName
    type: ParameterType
    optional: bool
    default: Optional[ParameterType]
    flag: str
    short_flag: str
    action: Literal["store", "store_true", "store_false"]
    help: str
    ui_exposed: bool
    plugin: PluginUrl


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
    parameters: PluginParametersUrl
    plugin_type: PluginType = serde.field(rename="type")

    @http.search("compute_resources", subpath="")
    def get_compute_resources(self) -> Search[ComputeResource]:
        """Get the compute resources this plugin is registered to."""
        ...

    @http.search("parameters", subpath="")
    def get_parameters(self) -> Search[PluginParameter]:
        """Get the parameters of this plugin."""
        ...

    async def print_help(self, out: TextIO = sys.stdout) -> None:
        """
        Display the help messages for this plugin's parameters.
        """
        async for param in self.get_parameters():
            left = f"{param.name} ({param.flag})"
            out.write(f"{left:>20}: {param.help}")
            if param.default is not None:
                out.write(f" (default: {param.default})")
            out.write("\n")
