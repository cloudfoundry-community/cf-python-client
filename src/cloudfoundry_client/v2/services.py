from cloudfoundry_client.entities import EntityManager


class ServiceManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(ServiceManager, self).__init__(target_endpoint, credentials_manager, '/v2/services')


