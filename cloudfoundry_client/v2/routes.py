from typing import Optional, TYPE_CHECKING

from cloudfoundry_client.v2.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class RouteManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(RouteManager, self).__init__(target_endpoint, client, "/v2/routes")

    def create_tcp_route(self, domain_guid: str, space_guid: str, port: Optional[int] = None) -> Entity:
        request = self._request(domain_guid=domain_guid, space_guid=space_guid)
        if port is None:
            return super(RouteManager, self)._create(request, params=dict(generate_port=True))
        else:
            request["port"] = port
            return super(RouteManager, self)._create(request)

    def create_host_route(self, domain_guid: str, space_guid: str, host: str, path: Optional[str] = "") -> Entity:
        request = dict(domain_guid=domain_guid, space_guid=space_guid, host=host, path=path)
        return super(RouteManager, self)._create(request)
