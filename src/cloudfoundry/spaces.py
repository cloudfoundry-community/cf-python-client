from cloudfoundry.entities import EntityManager


class SpaceManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(SpaceManager, self).__init__(target_endpoint, credentials_manager)

    def list(self, organization):
        for resource in super(SpaceManager, self)._list('%s%s' % (self.target_endpoint,
                                                                  organization['entity']['spaces_url'])):
            yield resource
