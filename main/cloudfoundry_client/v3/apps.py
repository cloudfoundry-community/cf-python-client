from cloudfoundry_client.v3.entities import EntityManager


class AppManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(AppManager, self).__init__(target_endpoint, client, '/v3/apps')

    def remove(self, application_guid):
        super(AppManager, self)._remove(application_guid)
