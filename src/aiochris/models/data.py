"""
Dataclasses describing objects returned from CUBE.

These classes are extended in the modules `aiochris.models.logged_in`
and `aiochris.models.public` with methods to get objects from links.
"""

from dataclasses import dataclass
import datetime
from typing import Optional

from serde import deserialize

from aiochris.link.linked import LinkedModel
from aiochris.enums import PluginType, Status
from aiochris.types import *


@deserialize
@dataclass(frozen=True)
class UserData:
    """A *CUBE* user."""

    url: UserUrl
    id: UserId
    username: Username
    email: str


# TODO It'd be better to use inheritance instead of optionals
@deserialize
@dataclass(frozen=True)
class PluginInstanceData(LinkedModel):
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
class FeedData(LinkedModel):
    url: FeedUrl
    id: FeedId
    creation_date: datetime.datetime
    modification_date: datetime.datetime
    name: str
    creator_username: Username
    created_jobs: int
    waiting_jobs: int
    scheduled_jobs: int
    started_jobs: int
    registering_jobs: int
    finished_jobs: int
    errored_jobs: int
    cancelled_jobs: int
    owner: list[UserUrl]
    note: NoteUrl
    tags: TagsUrl
    taggings: TaggingsUrl
    comments: CommentsUrl
    files: FilesUrl
    plugin_instances: PluginInstancesUrl


@deserialize
@dataclass(frozen=True)
class FeedNoteData(LinkedModel):
    url: FeedUrl
    id: NoteId
    title: str
    content: str
    feed: FeedUrl
