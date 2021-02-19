from typing import Optional, TYPE_CHECKING

from cloudfoundry_client.v2.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class ServiceBindingManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(ServiceBindingManager, self).__init__(target_endpoint, client, "/v2/service_bindings")

    def create(self, app_guid: str, instance_guid: str, parameters: Optional[dict] = None, name: Optional[str] = None) -> Entity:
        request = self._request(app_guid=app_guid, service_instance_guid=instance_guid)
        request["parameters"] = parameters
        request["name"] = name
        return super(ServiceBindingManager, self)._create(request)

    def remove(self, binding_id: str):
        super(ServiceBindingManager, self)._remove(binding_id)
