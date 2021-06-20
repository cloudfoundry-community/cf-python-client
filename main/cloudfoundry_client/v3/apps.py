from typing import TYPE_CHECKING, Optional

from cloudfoundry_client.json_object import JsonObject
from cloudfoundry_client.v3.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class App(Entity):
    @staticmethod
    def _manager_method(link_name: str, link_method: str) -> Optional[str]:
        if link_name == "environment_variables" and link_method == "get":
            return "_get"  # instead of _paginate
        return Entity._manager_method(link_name, link_method)


class AppManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(AppManager, self).__init__(target_endpoint, client, "/v3/apps", App)

    def remove(self, application_guid: str):
        super(AppManager, self)._remove(application_guid)

    def get_env(self, application_guid: str) -> JsonObject:
        return super(AppManager, self)._get("%s%s/%s/env" % (self.target_endpoint, self.entity_uri, application_guid))

    def get_routes(self, application_guid: str) -> JsonObject:
        return super(AppManager, self)._get("%s%s/%s/routes" % (self.target_endpoint, self.entity_uri, application_guid))
