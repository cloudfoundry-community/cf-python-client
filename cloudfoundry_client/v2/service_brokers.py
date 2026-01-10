from typing import TYPE_CHECKING

from cloudfoundry_client.v2.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class ServiceBrokerManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super().__init__(target_endpoint, client, "/v2/service_brokers")

    def create(
        self, broker_url: str, broker_name: str, auth_username: str, auth_password: str, space_guid: str | None = None
    ) -> Entity:
        request = self._request(broker_url=broker_url, name=broker_name, auth_username=auth_username, auth_password=auth_password)
        request["space_guid"] = space_guid
        return super()._create(request)

    def update(
        self,
        broker_guid: str,
        broker_url: str | None = None,
        broker_name: str | None = None,
        auth_username: str | None = None,
        auth_password: str | None = None,
    ) -> Entity:
        request = self._request()
        request["broker_url"] = broker_url
        request["name"] = broker_name
        request["auth_username"] = auth_username
        request["auth_password"] = auth_password
        return super()._update(broker_guid, request)

    def remove(self, broker_guid):
        super()._remove(broker_guid)
