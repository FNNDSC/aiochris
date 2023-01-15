from dataclasses import dataclass
from serde import deserialize
from chris.models.types import (
    UserUrl,
    UserId,
    Username,
    PluginName,
    ImageTag,
    PluginVersion,
    PluginUrl,
    PluginId,
)


@deserialize
@dataclass(frozen=True)
class Plugin:
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
