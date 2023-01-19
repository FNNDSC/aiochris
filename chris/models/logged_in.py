"""
Subclasses of classes from `chris.models.data` which are returned
from an `chris.client.authed.AuthenticatedClient`.
These classes may have read-write functionality on the *ChRIS* API.
"""
from dataclasses import dataclass
from typing import Optional

from serde import deserialize

from chris.link import http
from chris.link.linked import LinkedModel
from chris.models.data import PluginInstanceData, FeedData, UserData, FeedNoteData
from chris.models.enums import PluginType
from chris.models.public import PublicPlugin
from chris.models.types import *


@deserialize
@dataclass(frozen=True)
class User(UserData, LinkedModel):
    pass  # TODO change_email, change_password


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


@deserialize
@dataclass(frozen=True)
class PluginInstance(PluginInstanceData):
    @http.get("feed")
    async def get_feed(self) -> "Feed":
        """Get the feed this plugin instance belongs to."""
        ...

    @http.put("url")
    async def set(
        self, title: Optional[str] = None, status: Optional[str] = None
    ) -> "PluginInstance":
        """
        Set the title or status of this plugin instance.
        """
        ...


@deserialize
@dataclass(frozen=True)
class FeedNote(FeedNoteData):
    @http.get("feed")
    async def get_feed(self) -> "Feed":
        """Get the feed this note belongs to."""
        ...

    @http.put("url")
    async def set(
        self, title: Optional[str] = None, content: Optional[str] = None
    ) -> "FeedNote":
        """Change this note."""
        ...


@deserialize
@dataclass(frozen=True)
class Feed(FeedData):
    """
    A feed of a logged in user.
    """

    @http.put("url")
    def set(
        self, name: Optional[str] = None, owner: Optional[str | Username] = None
    ) -> "Feed":
        """
        Change the name or the owner of this feed.

        Parameters
        ----------
        name
            new name for this feed
        owner
            new owner for this feed
        """
        ...

    @http.get("note")
    def get_note(self) -> FeedNote:
        ...


@deserialize
@dataclass(frozen=True)
class Plugin(PublicPlugin):
    """
    A ChRIS plugin. Create a plugin instance of this plugin to run it.
    """

    instances: ApiUrl

    @http.post("instances")
    async def _create_instance_raw(self, **kwargs) -> PluginInstance:
        ...

    async def create_instance(
        self, previous: Optional[PluginInstance] = None, **kwargs
    ) -> PluginInstance:
        """
        Create a plugin instance, i.e. "run" this plugin.

        Parameters
        ----------
        previous
            Previous plugin instance
        """
        if previous is not None:
            if "previous_id" in kwargs:
                raise ValueError("Cannot give both previous and previous_id.")
            if not isinstance(previous, PluginInstance):
                raise TypeError(f"{previous} is not a PluginInstance")
            kwargs["previous_id"] = previous.id
        if self.plugin_type is PluginType.fs:
            if "previous_id" in kwargs:
                raise ValueError(
                    "Cannot create plugin instance of a fs-type plugin with a previous plugin instance."
                )
        elif "previous_id" not in kwargs:
            raise ValueError(
                f'Plugin type is "{self.plugin_type.value}" so previous is a required parameter.'
            )
        return await self._create_instance_raw(**kwargs)
