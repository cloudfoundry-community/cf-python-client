from typing import TYPE_CHECKING

from cloudfoundry_client.v3.entities import EntityManager, Entity, ToOneRelationship

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class ServiceBrokerManager(EntityManager[Entity]):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super().__init__(target_endpoint, client, "/v3/service_brokers")

    def create(
        self,
        name: str,
        url: str,
        auth_username: str,
        auth_password: str,
        space_guid: str | None = None,
        meta_labels: dict | None = None,
        meta_annotations: dict | None = None,
    ) -> Entity:
        credentials = {"type": "basic", "credentials": {"username": auth_username, "password": auth_password}}
        payload = dict(name=name, url=url, authentication=credentials)
        self._metadata(payload, meta_labels, meta_annotations)
        if space_guid:
            payload["relationships"] = dict(space=ToOneRelationship(space_guid))
        return super()._create(payload)

    def update(
        self,
        guid: str,
        name: str | None = None,
        url: str | None = None,
        auth_username: str | None = None,
        auth_password: str | None = None,
        meta_labels: dict | None = None,
        meta_annotations: dict | None = None,
    ) -> Entity:
        payload = dict()
        if name:
            payload["name"] = name
        if url:
            payload["url"] = url
        if auth_username and auth_password:
            payload["authentication"] = {"type": "basic", "credentials": {"username": auth_username, "password": auth_password}}
        self._metadata(payload, meta_labels, meta_annotations)
        return super()._update(guid, payload)

    def remove(self, guid: str, asynchronous: bool = True) -> str | None:
        return super()._remove(guid, asynchronous)
