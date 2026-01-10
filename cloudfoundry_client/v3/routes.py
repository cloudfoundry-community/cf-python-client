from enum import Enum
from typing import TYPE_CHECKING, Any

from cloudfoundry_client.v3.entities import EntityManager, Entity, ToOneRelationship

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class LoadBalancing(Enum):
    ROUND_ROBIN = 'round-robin'
    LEAST_CONNECTION = 'least-connection'


class RouteManager(EntityManager[Entity]):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super().__init__(target_endpoint, client, "/v3/routes")

    def create(self,
               space_guid: str,
               domain_guid: str,
               host: str | None = None,
               path: str | None = None,
               port: int | None = None,
               load_balancing: LoadBalancing | None = None,
               meta_labels: dict | None = None,
               meta_annotations: dict | None = None,
               ) -> Entity:
        data: dict[str, Any] = {
            "relationships": {
                "space": ToOneRelationship(space_guid), "domain": ToOneRelationship(domain_guid)
            },
        }
        if host is not None:
            data["host"] = host
        if port is not None:
            data["port"] = port
        if path is not None:
            data["path"] = path
        if load_balancing is not None:
            data["options"] = {"loadbalancing": load_balancing.value}
        self._metadata(data, meta_labels, meta_annotations)
        return super()._create(data)

    def update(self,
               route_gid: str,
               load_balancing: LoadBalancing | None = None,
               meta_labels: dict | None = None,
               meta_annotations: dict | None = None,
               ) -> Entity:
        data: dict[str, Any] = {}
        if load_balancing is not None:
            data["options"] = {"loadbalancing": load_balancing.value}
        self._metadata(data, meta_labels, meta_annotations)
        return super()._update(route_gid, data)

    def remove(self, route_gid: str):
        return super()._remove(route_gid)
