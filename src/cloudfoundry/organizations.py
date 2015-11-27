from cloudfoundry.entities import EntityManager


class OrganizationManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(OrganizationManager, self).__init__(target_endpoint, credentials_manager)

    def list(self):
        return self.credentials_manager.get('%s/v2/organizations' % self.target_endpoint)