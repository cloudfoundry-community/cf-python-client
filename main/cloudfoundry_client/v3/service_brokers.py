from typing import Optional, TYPE_CHECKING

from cloudfoundry_client.v3.entities import EntityManager, Entity, ToOneRelationship

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class ServiceBrokerManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(ServiceBrokerManager, self).__init__(target_endpoint, client, "/v3/service_brokers")

    def create(
        self,
        name: str,
        url: str,
        auth_username: str,
        auth_password: str,
        space_guid: Optional[str] = None,
        meta_labels: Optional[dict] = None,
        meta_annotations: Optional[dict] = None,
    ) -> Entity:
        credentials = {"type": "basic", "credentials": {"username": auth_username, "password": auth_password}}
        payload = dict(name=name, url=url, authentication=credentials)
        if meta_labels or meta_annotations:
            metadata = dict()
            if meta_labels:
                metadata["labels"] = meta_labels
            if meta_annotations:
                metadata["annotations"] = meta_annotations
            payload["metadata"] = metadata
        if space_guid:
            payload["relationships"] = dict(space=ToOneRelationship(space_guid))
        return super(ServiceBrokerManager, self)._create(payload)

    def update(
        self,
        guid: str,
        name: Optional[str] = None,
        url: Optional[str] = None,
        auth_username: Optional[str] = None,
        auth_password: Optional[str] = None,
        meta_labels: Optional[dict] = None,
        meta_annotations: Optional[dict] = None,
    ) -> Entity:
        payload = dict()
        if name:
            payload["name"] = name
        if url:
            payload["url"] = url
        if auth_username and auth_password:
            payload["authentication"] = {"type": "basic", "credentials": {"username": auth_username, "password": auth_password}}
        if meta_labels or meta_annotations:
            metadata = dict()
            if meta_labels:
                metadata["labels"] = meta_labels
            if meta_annotations:
                metadata["annotations"] = meta_annotations
            payload["metadata"] = metadata
        return super(ServiceBrokerManager, self)._update(guid, payload)

    def remove(self, guid: str):
        super(ServiceBrokerManager, self)._remove(guid)
