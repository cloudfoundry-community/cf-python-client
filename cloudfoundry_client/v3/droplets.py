from typing import TYPE_CHECKING, Any

from cloudfoundry_client.v3.entities import EntityManager, Entity, ToOneRelationship

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class DropletManager(EntityManager[Entity]):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super().__init__(target_endpoint, client, "/v3/droplets")

    def create(self,
               app_guid: str,
               process_types: dict[str, str] | None = None,
               meta_labels: dict | None = None,
               meta_annotations: dict | None = None,
               ) -> Entity:
        data: dict[str, Any] = {
            "relationships": {
                "app": ToOneRelationship(app_guid)
            },
        }
        if process_types is not None:
            data["process_types"] = process_types
        self._metadata(data, meta_labels, meta_annotations)
        return super()._create(data)

    def copy(self,
             droplet_guid: str,
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
            source_guid=droplet_guid
        )
        return self._post(url, data=data)

    def update(self,
               droplet_gid: str,
               meta_labels: dict | None = None,
               meta_annotations: dict | None = None,
               ) -> Entity:
        data: dict[str, Any] = {}
        self._metadata(data, meta_labels, meta_annotations)
        return super()._update(droplet_gid, data)

    def remove(self, route_gid: str):
        return super()._remove(route_gid)
