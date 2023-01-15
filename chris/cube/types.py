from dataclasses import dataclass
from typing import NewType

from serde import deserialize

AdminUrl = NewType("AdminUrl", str)
ComputeResourceName = NewType("ComputeResourceName", str)
ComputeResourceId = NewType("ComputeResourceId", str)

PfconUrl = NewType("PfconUrl", str)

FeedId = NewType("FeedId", str)


@deserialize
@dataclass(frozen=True)
class Feed:
    id: FeedId
    name: str
