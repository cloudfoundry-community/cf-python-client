from typing import TYPE_CHECKING

from cloudfoundry_client.v3.entities import EntityManager

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class ServiceInstanceManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(ServiceInstanceManager, self).__init__(target_endpoint, client, "/v3/service_instances")

    def remove(self, guid: str, asynchronous: bool = True):
        super(ServiceInstanceManager, self)._remove(guid, asynchronous)
