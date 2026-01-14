from typing import TYPE_CHECKING

from cloudfoundry_client.common_objects import Pagination
from cloudfoundry_client.v3.entities import EntityManager, Entity, ToOneRelationship

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class OrganizationManager(EntityManager[Entity]):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super().__init__(target_endpoint, client, "/v3/organizations")

    def create(
        self, name: str, suspended: bool, meta_labels: dict | None = None, meta_annotations: dict | None = None
    ) -> Entity:
        data = {"name": name, "suspended": suspended}
        self._metadata(data, meta_labels, meta_annotations)
        return super()._create(data)

    def update(
        self,
        guid: str,
        name: str,
        suspended: bool | None = None,
        meta_labels: dict | None = None,
        meta_annotations: dict | None = None,
    ) -> Entity:
        data = {"name": name}
        if suspended is not None:
            data["suspended"] = suspended
        self._metadata(data, meta_labels, meta_annotations)
        return super()._update(guid, data)

    def remove(self, guid: str, asynchronous: bool = True) -> str | None:
        return super()._remove(guid, asynchronous)

    def assign_default_isolation_segment(self, org_guid: str, iso_seg_guid: str) -> Entity:
        return ToOneRelationship.from_json_object(
            super()._patch(
                "%s%s/%s/relationships/default_isolation_segment" % (self.target_endpoint, self.entity_uri, org_guid),
                data=ToOneRelationship(iso_seg_guid),
            )
        )

    def get_default_isolation_segment(self, guid: str) -> ToOneRelationship:
        return ToOneRelationship.from_json_object(
            super().get(guid, "relationships", "default_isolation_segment")
        )

    def list_domains(self, guid: str, **kwargs) -> Pagination[Entity]:
        uri: str = "%s/%s/domains" % (self.entity_uri, guid)
        return super()._list(requested_path=uri, **kwargs)

    def get_default_domain(self, guid: str) -> Entity:
        return super().get(guid, "domains", "default")

    def get_usage_summary(self, guid: str) -> Entity:
        return super().get(guid, "usage_summary")
