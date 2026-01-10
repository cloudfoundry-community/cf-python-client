from typing import TYPE_CHECKING

from cloudfoundry_client.v2.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class ServiceInstanceManager(EntityManager):
    list_query_parameters = ["page", "results-per-page", "order-direction", "return_user_provided_service_instances"]

    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super().__init__(target_endpoint, client, "/v2/service_instances")

    def create(
        self,
        space_guid: str,
        instance_name: str,
        plan_guid: str,
        parameters: dict | None = None,
        tags: list[str] = None,
        accepts_incomplete: bool | None = False,
    ) -> Entity:
        request = self._request(name=instance_name, space_guid=space_guid, service_plan_guid=plan_guid)
        request["parameters"] = parameters
        request["tags"] = tags
        params = None if not accepts_incomplete else dict(accepts_incomplete="true")
        return super()._create(request, params=params)

    def update(
        self,
        instance_guid: str,
        instance_name: str | None = None,
        plan_guid: str | None = None,
        parameters: dict | None = None,
        tags: list[str] = None,
        accepts_incomplete: bool | None = False,
    ) -> Entity:
        request = self._request()
        request["name"] = instance_name
        request["service_plan_guid"] = plan_guid
        request["parameters"] = parameters
        request["tags"] = tags
        params = None if not accepts_incomplete else dict(accepts_incomplete="true")
        return super()._update(instance_guid, request, params=params)

    def list_permissions(self, instance_guid: str) -> dict[str, bool]:
        return super()._get("%s/%s/permissions" % (self.entity_uri, instance_guid), dict)

    def remove(self, instance_guid: str, accepts_incomplete: bool | None = False, purge: bool | None = False):
        parameters = {}
        if accepts_incomplete:
            parameters["accepts_incomplete"] = "true"
        if purge:
            parameters["purge"] = "true"
        super()._remove(instance_guid, params=parameters)
