from typing import Optional, TYPE_CHECKING, List

from cloudfoundry_client.v3.entities import Entity, EntityManager, ToOneRelationship

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class ServiceInstanceManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(ServiceInstanceManager, self).__init__(target_endpoint, client, "/v3/service_instances")

    def create(
        self,
        name: str,
        space_guid: str,
        service_plan_guid: str,
        meta_labels: Optional[dict] = None,
        meta_annotations: Optional[dict] = None,
        parameters: Optional[dict] = None,
        tags: Optional[List[str]] = None,
    ) -> Entity:
        data = {
            "name": name,
            "type": "managed",
            "relationships": {"space": ToOneRelationship(space_guid), "service_plan": ToOneRelationship(service_plan_guid)},
        }
        if parameters:
            data["parameters"] = parameters
        if tags:
            data["tags"] = tags
        if meta_labels or meta_annotations:
            metadata = dict()
            if meta_labels:
                metadata["labels"] = meta_labels
            if meta_annotations:
                metadata["annotations"] = meta_annotations
            data["metadata"] = metadata
        return super(ServiceInstanceManager, self)._create(data)

    def remove(self, guid: str, asynchronous: bool = True):
        super(ServiceInstanceManager, self)._remove(guid, asynchronous)
