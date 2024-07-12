from typing import TYPE_CHECKING

from cloudfoundry_client.v2.entities import EntityManager

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class SpaceManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(SpaceManager, self).__init__(target_endpoint, client, "/v2/spaces")

    def delete_unmapped_routes(self, space_guid: str):
        url = "%s%s/%s/unmapped_routes" % (self.target_endpoint, self.entity_uri, space_guid)
        super(SpaceManager, self)._delete(url)
