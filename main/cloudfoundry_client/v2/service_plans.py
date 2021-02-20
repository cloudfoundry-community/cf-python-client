from typing import TYPE_CHECKING

from cloudfoundry_client.v2.entities import EntityManager, Entity, PaginateEntities

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class ServicePlanManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(ServicePlanManager, self).__init__(target_endpoint, client, "/v2/service_plans")

    def create_from_resource_file(self, path: str) -> Entity:
        raise NotImplementedError("No creation allowed")

    def list_instances(self, service_plan_guid: str, **kwargs) -> PaginateEntities:
        return self.client.v2.service_instances._list("%s/%s/service_instances" % (self.entity_uri, service_plan_guid), **kwargs)
