from cloudfoundry_client.entities import Entity, EntityManager


class RouteManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(RouteManager, self).__init__(target_endpoint, client, '/v2/routes',
                                           lambda pairs: Entity(client, pairs))
