from typing import TYPE_CHECKING

from cloudfoundry_client.v2.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class ServiceBindingManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super().__init__(target_endpoint, client, "/v2/service_bindings")

    def create(self, app_guid: str, instance_guid: str, parameters: dict | None = None, name: str | None = None) -> Entity:
        request = self._request(app_guid=app_guid, service_instance_guid=instance_guid)
        request["parameters"] = parameters
        request["name"] = name
        return super()._create(request)

    def remove(self, binding_id: str):
        super()._remove(binding_id)
