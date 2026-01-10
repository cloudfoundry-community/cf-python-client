from enum import Enum
from typing import TYPE_CHECKING, Any

from cloudfoundry_client.common_objects import Pagination
from cloudfoundry_client.v3.entities import EntityManager, Entity, ToOneRelationship

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class PackageType(Enum):
    BITS = 'bits'
    DOCKER = 'docker'


class PackageManager(EntityManager[Entity]):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super().__init__(target_endpoint, client, "/v3/packages")

    def create(self,
               app_guid: str,
               package_type: PackageType,
               meta_labels: dict | None = None,
               meta_annotations: dict | None = None,
               ) -> Entity:
        data: dict[str, Any] = {
            "type": package_type.value,
            "relationships": {
                "app": ToOneRelationship(app_guid)
            },
        }
        self._metadata(data, meta_labels, meta_annotations)
        return super()._create(data)

    def copy(self,
             package_guid: str,
             app_guid: str,
             meta_labels: dict | None = None,
             meta_annotations: dict | None = None,
             ) -> Entity:
        data: dict[str, Any] = {
            "relationships": {
                "app": ToOneRelationship(app_guid)
            },
        }
        self._metadata(data, meta_labels, meta_annotations)
        url = EntityManager._get_url_with_encoded_params(
            "%s%s" % (self.target_endpoint, self.entity_uri),
            source_guid=package_guid
        )
        return self._post(url, data=data)

    def list_droplets(self, package_guid: str, **kwargs) -> Pagination[Entity]:
        uri: str = "%s/%s/droplets" % (self.entity_uri, package_guid)
        return super()._list(requested_path=uri, **kwargs)
