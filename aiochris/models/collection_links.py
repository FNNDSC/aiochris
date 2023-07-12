import dataclasses
import functools
from dataclasses import dataclass
from typing import Iterator

from serde import deserialize

from aiochris.types import ApiUrl, UserUrl, AdminUrl


@deserialize
@dataclass(frozen=True)
class AbstractCollectionLinks:
    @classmethod
    def has_field(cls, field_name: str) -> bool:
        return field_name in cls._field_names()

    @classmethod
    def _field_names(cls) -> Iterator[str]:
        return (f.name for f in dataclasses.fields(cls))

    def get(self, collection_name: str) -> str:
        url = self._dict.get(collection_name, None)
        if url is None:
            raise TypeError(
                f'{self.__class__} does not have link for "{collection_name}"'
            )
        return url

    @functools.cached_property
    def _dict(self) -> dict[str, str]:
        return dataclasses.asdict(self)


@deserialize
@dataclass(frozen=True)
class AnonymousCollectionLinks(AbstractCollectionLinks):
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


@deserialize
@dataclass(frozen=True)
class AdminApiCollectionLinks(AbstractCollectionLinks):
    compute_resources: ApiUrl
