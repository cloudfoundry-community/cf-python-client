from typing import Optional, TYPE_CHECKING

from cloudfoundry_client.v3.entities import EntityManager, Entity, ToManyRelationship

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class IsolationSegmentManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(IsolationSegmentManager, self).__init__(target_endpoint, client, "/v3/isolation_segments")

    def create(self, name: str, meta_labels: Optional[dict] = None, meta_annotations: Optional[dict] = None) -> Entity:
        data = {"name": name, "metadata": {"labels": meta_labels, "annotations": meta_annotations}}
        return super(IsolationSegmentManager, self)._create(data)

    def update(
        self, isolation_segment_guid: str, name: str, meta_labels: Optional[dict] = None, meta_annotations: Optional[dict] = None
    ) -> Entity:
        data = {"name": name, "metadata": {"labels": meta_labels, "annotations": meta_annotations}}
        return super(IsolationSegmentManager, self)._update(isolation_segment_guid, data)

    def entitle_organizations(self, isolation_segment_guid: str, *org_guids: str) -> ToManyRelationship:
        data = ToManyRelationship(*org_guids)
        return ToManyRelationship.from_json_object(
            super(IsolationSegmentManager, self)._post(
                "%s%s/%s/relationships/organizations" % (self.target_endpoint, self.entity_uri, isolation_segment_guid), data=data
            )
        )

    def list_entitled_organizations(
        self,
        isolation_segment_guid: str,
    ) -> ToManyRelationship:
        return ToManyRelationship.from_json_object(
            super(IsolationSegmentManager, self)._get(
                "%s%s/%s/relationships/organizations" % (self.target_endpoint, self.entity_uri, isolation_segment_guid)
            )
        )

    def list_entitled_spaces(
        self,
        isolation_segment_guid: str,
    ) -> ToManyRelationship:
        return ToManyRelationship.from_json_object(
            super(IsolationSegmentManager, self)._get(
                "%s%s/%s/relationships/spaces" % (self.target_endpoint, self.entity_uri, isolation_segment_guid)
            )
        )

    def revoke_organization(self, isolation_segment_guid: str, org_guid: str):
        super(IsolationSegmentManager, self)._delete(
            "%s%s/%s/relationships/organizations/%s" % (self.target_endpoint, self.entity_uri, isolation_segment_guid, org_guid)
        )

    def remove(self, isolation_segment_guid: str):
        super(IsolationSegmentManager, self)._remove(isolation_segment_guid)
