import functools
from typing import TYPE_CHECKING

from cloudfoundry_client.json_object import JsonObject
from cloudfoundry_client.v3.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class App(Entity):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient", **kwargs):
        super(App, self).__init__(target_endpoint, client, **kwargs)
        # patch environment_variables method
        environment_variables_link = self.get("links", {}).get("environment_variables", {}).get("href", None)
        if environment_variables_link is not None:
            other_manager = self._default_manager(client, target_endpoint)
            new_method = functools.partial(other_manager._get, environment_variables_link)
            new_method.__name__ = "environment_variables"
            setattr(self, "environment_variables", new_method)


class AppManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(AppManager, self).__init__(target_endpoint, client, "/v3/apps", App)

    def remove(self, application_guid: str):
        super(AppManager, self)._remove(application_guid)

    def get_env(self, application_guid: str) -> JsonObject:
        return super(AppManager, self)._get("%s%s/%s/env" % (self.target_endpoint, self.entity_uri, application_guid))

    def get_routes(self, application_guid: str) -> JsonObject:
        return super(AppManager, self)._get("%s%s/%s/routes" % (self.target_endpoint, self.entity_uri, application_guid))
