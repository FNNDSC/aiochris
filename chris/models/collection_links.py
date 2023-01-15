from dataclasses import dataclass

from serde import deserialize

from chris._old.types import AdminUrl
from chris.models.types import ApiUrl, UserUrl


@deserialize
@dataclass(frozen=True)
class AnonymousCollectionLinks:
    chrisinstance: ApiUrl
    files: ApiUrl
    compute_resources: ApiUrl
    plugin_metas: ApiUrl
    plugins: ApiUrl
    plugin_instances: ApiUrl
    pipelines: ApiUrl
    pipeline_instances: ApiUrl
    workflows: ApiUrl
    tags: ApiUrl
    uploadedfiles: ApiUrl
    pacsfiles: ApiUrl
    servicefiles: ApiUrl
    filebrowser: ApiUrl


@deserialize
@dataclass(frozen=True)
class CollectionLinks(AnonymousCollectionLinks):
    user: UserUrl


@deserialize
@dataclass(frozen=True)
class AdminCollectionLinks(CollectionLinks):
    admin: AdminUrl
