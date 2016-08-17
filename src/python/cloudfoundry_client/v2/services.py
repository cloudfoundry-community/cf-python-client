from cloudfoundry_client.entities import Entity, EntityManager


class ServiceManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(ServiceManager, self).__init__(target_endpoint, client, '/v2/services',
                                             lambda pairs: Entity(target_endpoint, client, pairs))
