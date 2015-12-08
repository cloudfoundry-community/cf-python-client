from cloudfoundry_client.entities import EntityManager


class OrganizationManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(OrganizationManager, self).__init__(target_endpoint, credentials_manager, '/v2/organizations')
