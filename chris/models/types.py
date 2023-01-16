"""
NewTypes for ChRIS models.
"""

from typing import NewType

Username = NewType("ChrisUsername", str)
Password = NewType("ChrisPassword", str)
ChrisURL = NewType("ChrisURL", str)

ApiUrl = NewType("ApiUrl", str)
"""URL which I am too lazy to be more specific about."""
ResourceId = NewType("ResourceId", int)
"""ID number which I am too lazy to be more specific about."""
PluginName = NewType("PluginName", str)
ImageTag = NewType("ImageTag", str)
PluginVersion = NewType("PluginVersion", str)

PluginUrl = NewType("PluginUrl", str)
PluginSearchUrl = NewType("PluginSearchUrl", str)

PluginId = NewType("PluginId", int)

UserUrl = NewType("UserUrl", str)
UserId = NewType("UserId", int)

AdminUrl = NewType("AdminUrl", str)
"""A admin resource URL ending with `/chris-admin/api/v1/`"""
ComputeResourceName = NewType("ComputeResourceName", str)
ComputeResourceId = NewType("ComputeResourceId", str)

PfconUrl = NewType("PfconUrl", str)

FeedId = NewType("FeedId", str)
