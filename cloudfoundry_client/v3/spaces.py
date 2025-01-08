from typing import Optional, TYPE_CHECKING

from cloudfoundry_client.v3.entities import EntityManager, ToOneRelationship, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class SpaceManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(SpaceManager, self).__init__(target_endpoint, client, "/v3/spaces")

    def create(self, name: str, org_guid: str) -> Entity:
        return super(SpaceManager, self)._create(dict(name=name, relationships=dict(organization=ToOneRelationship(org_guid))))

    def update(self, space_guid: str, name: str) -> Entity:
        return super(SpaceManager, self)._update(space_guid, dict(name=name))

    def get_assigned_isolation_segment(self, space_guid: str) -> ToOneRelationship:
        return ToOneRelationship.from_json_object(
            super(SpaceManager, self)._get(
                "%s%s/%s/relationships/isolation_segment" % (self.target_endpoint, self.entity_uri, space_guid)
            )
        )

    def assign_isolation_segment(self, space_guid: str, isolation_segment_guid: Optional[str]) -> ToOneRelationship:
        return ToOneRelationship.from_json_object(
            super(SpaceManager, self)._patch(
                "%s%s/%s/relationships/isolation_segment" % (self.target_endpoint, self.entity_uri, space_guid),
                dict(data=None) if isolation_segment_guid is None else ToOneRelationship(isolation_segment_guid),
            )
        )

    def remove(self, space_guid: str):
        super(SpaceManager, self)._remove(space_guid)
