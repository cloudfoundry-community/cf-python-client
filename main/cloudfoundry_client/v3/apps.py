from cloudfoundry_client.json_object import JsonObject
from cloudfoundry_client.v3.entities import EntityManager


class AppManager(EntityManager):
    def __init__(self, target_endpoint: str, client: 'CloudfoundryClient'):
        super(AppManager, self).__init__(target_endpoint, client, '/v3/apps')

    def remove(self, application_guid: str):
        super(AppManager, self)._remove(application_guid)

    def get_env(self, application_guid: str) -> JsonObject:
        return super(AppManager, self)._get('%s%s/%s/env' % (self.target_endpoint, self.entity_uri, application_guid))

    def get_routes(self, application_guid: str) -> JsonObject:
        return super(AppManager, self)._get('%s%s/%s/routes' % (self.target_endpoint, self.entity_uri, application_guid))
