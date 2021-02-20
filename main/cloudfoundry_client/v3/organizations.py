from typing import Optional, TYPE_CHECKING

from cloudfoundry_client.v3.entities import EntityManager, Entity, ToOneRelationship

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class OrganizationManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(OrganizationManager, self).__init__(target_endpoint, client, "/v3/organizations")

    def create(
        self, name: str, suspended: bool, meta_labels: Optional[dict] = None, meta_annotations: Optional[dict] = None
    ) -> Entity:
        data = {"name": name, "suspended": suspended, "metadata": {"labels": meta_labels, "annotations": meta_annotations}}
        return super(OrganizationManager, self)._create(data)

    def update(
        self,
        guid: str,
        name: str,
        suspended: Optional[bool],
        meta_labels: Optional[dict] = None,
        meta_annotations: Optional[dict] = None,
    ) -> Entity:
        data = {"name": name, "suspended": suspended, "metadata": {"labels": meta_labels, "annotations": meta_annotations}}
        return super(OrganizationManager, self)._update(guid, data)

    def remove(self, guid: str):
        super(OrganizationManager, self)._remove(guid)

    def assign_default_isolation_segment(self, org_guid: str, iso_seg_guid: str) -> Entity:
        return ToOneRelationship.from_json_object(
            super(OrganizationManager, self)._patch(
                "%s%s/%s/relationships/default_isolation_segment" % (self.target_endpoint, self.entity_uri, org_guid),
                data=ToOneRelationship(iso_seg_guid),
            )
        )

    def get_default_isolation_segment(self, guid: str) -> ToOneRelationship:
        return ToOneRelationship.from_json_object(
            super(OrganizationManager, self).get(guid, "relationships", "default_isolation_segment")
        )

    def get_default_domain(self, guid: str) -> Entity:
        return super(OrganizationManager, self).get(guid, "domains", "default")

    def get_usage_summary(self, guid: str) -> Entity:
        return super(OrganizationManager, self).get(guid, "usage_summary")
