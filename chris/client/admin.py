from chris.client.authed import AuthenticatedClient
from chris.models.collection_links import AdminCollectionLinks


class ChrisAdminClient(AuthenticatedClient[AdminCollectionLinks, "ChrisAdminClient"]):
    """
    A client who has access to `/chris-admin/`. Admins can register new plugins and
    add new compute resources.
    """

    pass
