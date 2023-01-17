from dataclasses import dataclass
from serde import deserialize

from chris.models.connected import Connected
from chris.models.types import (
    UserUrl,
    UserId,
    Username,
    PluginName,
    ImageTag,
    PluginVersion,
    PluginUrl,
    PluginId,
    FeedId,
    ApiUrl,
    ComputeResourceId,
    ComputeResourceName,
    PfconUrl,
)


@deserialize
@dataclass(frozen=True)
class Plugin(Connected):
    url: PluginUrl
    id: PluginId
    name: PluginName
    version: PluginVersion
    dock_image: ImageTag
    public_repo: str


@deserialize
@dataclass(frozen=True)
class User:
    url: UserUrl
    id: UserId
    username: Username
    email: str


@deserialize
@dataclass(frozen=True)
class Feed:
    id: FeedId
    name: str


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
