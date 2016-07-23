from cloudfoundry_client.entities import EntityManager


class RouteManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(RouteManager, self).__init__(target_endpoint, credentials_manager, '/v2/routes')
