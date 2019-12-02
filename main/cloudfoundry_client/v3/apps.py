from cloudfoundry_client.v3.entities import EntityManager


class AppManager(EntityManager):
    def __init__(self, target_endpoint: str, client: 'CloudfoundryClient'):
        super(AppManager, self).__init__(target_endpoint, client, '/v3/apps')

    def remove(self, application_guid: str):
        super(AppManager, self)._remove(application_guid)
