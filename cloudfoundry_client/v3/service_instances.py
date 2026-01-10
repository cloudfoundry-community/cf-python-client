from typing import TYPE_CHECKING

from cloudfoundry_client.common_objects import JsonObject
from cloudfoundry_client.v3.entities import Entity, EntityManager, ToOneRelationship

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class ServiceInstanceManager(EntityManager[Entity]):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super().__init__(target_endpoint, client, "/v3/service_instances")

    def create(
        self,
        name: str,
        space_guid: str,
        service_plan_guid: str,
        meta_labels: dict | None = None,
        meta_annotations: dict | None = None,
        parameters: dict | None = None,
        tags: list[str] | None = None,
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
        self._metadata(data, meta_labels, meta_annotations)
        return super()._create(data)

    def update(
            self,
            instance_guid: str,
            name: str | None = None,
            parameters: dict | None = None,
            service_plan: str | None = None,
            maintenance_info: str | None = None,
            meta_labels: dict | None = None,
            meta_annotations: dict | None = None,
            tags: list[str] | None = None
    ) -> Entity:
        data = {}
        if name:
            data["name"] = name
        if parameters:
            data["parameters"] = parameters
        if service_plan:
            data["relationships"] = {
                "service_plan": ToOneRelationship(service_plan)}
        if maintenance_info:
            data["maintenance_info"] = {"version": maintenance_info}
        if tags:
            data["tags"] = tags
        super()._metadata(data, meta_labels, meta_annotations)
        return super()._update(instance_guid, data)

    def remove(self, guid: str, asynchronous: bool = True):
        super()._remove(guid, asynchronous)

    def get_permissions(self, instance_guid: str) -> JsonObject:
        return super()._get(
            "%s%s/%s/permissions" % (self.target_endpoint, self.entity_uri, instance_guid)
        )
