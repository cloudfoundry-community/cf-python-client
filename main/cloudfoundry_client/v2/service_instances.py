from typing import Optional, List, Dict, TYPE_CHECKING

from cloudfoundry_client.v2.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class ServiceInstanceManager(EntityManager):
    list_query_parameters = ["page", "results-per-page", "order-direction", "return_user_provided_service_instances"]

    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(ServiceInstanceManager, self).__init__(target_endpoint, client, "/v2/service_instances")

    def create(
        self,
        space_guid: str,
        instance_name: str,
        plan_guid: str,
        parameters: Optional[dict] = None,
        tags: List[str] = None,
        accepts_incomplete: Optional[bool] = False,
    ) -> Entity:
        request = self._request(name=instance_name, space_guid=space_guid, service_plan_guid=plan_guid)
        request["parameters"] = parameters
        request["tags"] = tags
        params = None if not accepts_incomplete else dict(accepts_incomplete="true")
        return super(ServiceInstanceManager, self)._create(request, params=params)

    def update(
        self,
        instance_guid: str,
        instance_name: Optional[str] = None,
        plan_guid: Optional[str] = None,
        parameters: Optional[dict] = None,
        tags: List[str] = None,
        accepts_incomplete: Optional[bool] = False,
    ) -> Entity:
        request = self._request()
        request["name"] = instance_name
        request["service_plan_guid"] = plan_guid
        request["parameters"] = parameters
        request["tags"] = tags
        params = None if not accepts_incomplete else dict(accepts_incomplete="true")
        return super(ServiceInstanceManager, self)._update(instance_guid, request, params=params)

    def list_permissions(self, instance_guid: str) -> Dict[str, bool]:
        return super(ServiceInstanceManager, self)._get("%s/%s/permissions" % (self.entity_uri, instance_guid), dict)

    def remove(self, instance_guid: str, accepts_incomplete: Optional[bool] = False, purge: Optional[bool] = False):
        parameters = {}
        if accepts_incomplete:
            parameters["accepts_incomplete"] = "true"
        if purge:
            parameters["purge"] = "true"
        super(ServiceInstanceManager, self)._remove(instance_guid, params=parameters)
