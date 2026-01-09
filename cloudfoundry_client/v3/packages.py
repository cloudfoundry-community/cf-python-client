from typing import TYPE_CHECKING

from cloudfoundry_client.common_objects import Pagination
from cloudfoundry_client.v3.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class PackageManager(EntityManager[Entity]):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(PackageManager, self).__init__(target_endpoint, client, "/v3/packages")

    def list_droplets(self, package_guid: str, **kwargs) -> Pagination[Entity]:
        uri: str = "%s/%s/droplets" % (self.entity_uri, package_guid)
        return super(PackageManager, self)._list(requested_path=uri, **kwargs)
