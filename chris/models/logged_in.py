"""
Subclasses of classes from `chris.models.public` which are returned
from an `chris.client.authed.AuthenticatedClient`. In contrast,
these classes have read-write functionality on the *ChRIS* API.
"""
from dataclasses import dataclass
from typing import Optional
import datetime

from serde import deserialize

from chris.link import http
from chris.link.linked import LinkedModel
from chris.models.enums import PluginType
from chris.models.public import PublicPlugin
from chris.models.types import (
    PluginInstanceUrl,
    PluginInstanceId,
    ComputeResourceName,
    PluginId,
    PluginName,
    PluginVersion,
    FeedId,
    CubeFilePath,
    Username,
    CUBEErrorCode,
    FeedUrl,
    PluginUrl,
    DescendantsUrl,
    FilesUrl,
    PluginInstanceParamtersUrl,
    ComputeResourceUrl,
    SplitsUrl,
    ApiUrl,
    FileResourceUrl,
    FileFname,
)
from chris.models.enums import Status


# TODO It'd be better to use inheritance instead of optionals
@deserialize
@dataclass(frozen=True)
class PluginInstance(LinkedModel):
    """
    A *plugin instance* in _ChRIS_ is a computing job, i.e. an attempt to run
    a computation (a non-interactive command-line app) to produce data.
    """

    url: PluginInstanceUrl
    id: PluginInstanceId
    title: str
    compute_resource_name: ComputeResourceName
    plugin_id: PluginId
    plugin_name: PluginName
    plugin_version: PluginVersion
    plugin_type: PluginType

    pipeline_inst: Optional[int]
    feed_id: FeedId
    start_date: datetime.datetime
    end_date: datetime.datetime
    output_path: CubeFilePath

    status: Status

    summary: str
    raw: str
    owner_username: Username
    cpu_limit: int
    memory_limit: int
    number_of_workers: int
    gpu_limit: int
    error_code: CUBEErrorCode

    previous: Optional[PluginInstanceUrl]
    feed: FeedUrl
    plugin: PluginUrl
    descendants: DescendantsUrl
    files: FilesUrl
    parameters: PluginInstanceParamtersUrl
    compute_resource: ComputeResourceUrl
    splits: SplitsUrl

    previous_id: Optional[int] = None
    """
    FS plugins will not produce a `previous_id` value
    (even though they will return `"previous": null`)
    """

    size: Optional[int] = None
    """
    IDK what it is the size of.

    This field shows up when the plugin instance is maybe done,
    but not when the plugin instance is created.
    """
    template: Optional[dict] = None
    """
    Present only when getting a plugin instance.
    """


@deserialize
@dataclass(frozen=True)
class Plugin(PublicPlugin):
    """
    A ChRIS plugin. Create a plugin instance of this plugin to run it.
    """

    instances: ApiUrl

    @http.post("instances")
    async def create_instance(self, **kwargs) -> PluginInstance:
        ...


@deserialize
@dataclass(frozen=True)
class File(LinkedModel):
    """
    A file in CUBE.
    """

    url: str
    fname: FileFname
    fsize: int
    file_resource: FileResourceUrl

    @property
    def parent(self) -> str:
        """
        Get the parent (directory) of a file.

        Examples
        --------

        ```python
        assert file.fname == 'chris/feed_4/pl-dircopy_7/data/hello-world.txt'
        assert file.parent == 'chris/feed_4/pl-dircopy_7/data'
        ```
        """
        split = self.fname.split("/")
        if len(split) <= 1:
            return self.fname
        return "/".join(split[:-1])

    # TODO download methods
