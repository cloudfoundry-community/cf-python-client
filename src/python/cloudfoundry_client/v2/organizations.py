from cloudfoundry_client.entities import Entity, EntityManager


class OrganizationManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(OrganizationManager, self).__init__(target_endpoint, client, '/v2/organizations',
                                                  lambda pairs: Entity(client, pairs))
