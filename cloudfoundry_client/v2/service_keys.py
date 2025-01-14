from typing import Optional, TYPE_CHECKING

from cloudfoundry_client.v2.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class ServiceKeyManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(ServiceKeyManager, self).__init__(target_endpoint, client, "/v2/service_keys")

    def create(self, service_instance_guid: str, name: str, parameters: Optional[dict] = None) -> Entity:
        request = self._request(service_instance_guid=service_instance_guid, name=name)
        request["parameters"] = parameters
        return super(ServiceKeyManager, self)._create(request)

    def remove(self, key_guid: str):
        super(ServiceKeyManager, self)._remove(key_guid)
