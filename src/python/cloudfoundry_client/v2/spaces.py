from cloudfoundry_client.entities import Entity, EntityManager


class SpaceManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(SpaceManager, self).__init__(target_endpoint, client, '/v2/spaces',
                                           lambda pairs: Entity(target_endpoint, client, pairs))
