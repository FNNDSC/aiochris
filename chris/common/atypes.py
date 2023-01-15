from dataclasses import dataclass
from serde import deserialize
from chris.common.types import ApiUrl, UserUrl


@deserialize
@dataclass(frozen=True)
class CommonCollectionLinks:
    plugins: ApiUrl
    pipelines: ApiUrl


@deserialize
@dataclass(frozen=True)
class AuthenticatedCollectionLinks(CommonCollectionLinks):
    user: UserUrl
