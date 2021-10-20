from typing import TYPE_CHECKING

from cloudfoundry_client.json_object import JsonObject
from cloudfoundry_client.v3.entities import EntityManager

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class AppManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(AppManager, self).__init__(target_endpoint, client, "/v3/apps")

    def restart(self, application_guid: str):
        return super(AppManager, self)._post("%s%s/%s/actions/restart" % (self.target_endpoint,
                                                                          self.entity_uri,
                                                                          application_guid))

    def remove(self, application_guid: str):
        super(AppManager, self)._remove(application_guid)

    def get_env(self, application_guid: str) -> JsonObject:
        return super(AppManager, self)._get("%s%s/%s/env" % (self.target_endpoint, self.entity_uri, application_guid))

    def get_routes(self, application_guid: str) -> JsonObject:
        return super(AppManager, self)._get("%s%s/%s/routes" % (self.target_endpoint, self.entity_uri, application_guid))
