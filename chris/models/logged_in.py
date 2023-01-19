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
    async def create_instance(self, **kwargs) -> PluginInstance:
        ...
