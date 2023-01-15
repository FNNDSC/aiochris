"""
Be careful: types between _CUBE_ and _ChRIS_ store are not interoperable.
For instance, a `PluginId` from the _ChRIS_ store is meaningless in _CUBE_.
"""

from typing import NewType

ChrisUsername = NewType("ChrisUsername", str)
ChrisPassword = NewType("ChrisPassword", str)
ChrisURL = NewType("ChrisURL", str)
ChrisToken = NewType("ChrisToken", str)

ApiUrl = NewType("ApiUrl", str)
ResourceId = NewType("ResourceId", int)

PluginName = NewType("PluginName", str)
ImageTag = NewType("ImageTag", str)
PluginVersion = NewType("PluginVersion", str)

PluginUrl = NewType("PluginUrl", str)
PluginSearchUrl = NewType("PluginSearchUrl", str)

PluginId = NewType("PluginId", int)

UserUrl = NewType("UserUrl", str)
UserId = NewType("UserId", int)
