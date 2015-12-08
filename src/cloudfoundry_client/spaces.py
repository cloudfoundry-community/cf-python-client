from cloudfoundry_client.entities import EntityManager


class SpaceManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(SpaceManager, self).__init__(target_endpoint, credentials_manager, '/v2/spaces')

