from cloudfoundry_client.entities import EntityManager


class SpaceManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(SpaceManager, self).__init__(target_endpoint, credentials_manager)

    def list(self, org_uid):
        for resource in super(SpaceManager, self)._list('%s/v2/organizations/%s/spaces' % (self.target_endpoint,
                                                                                           org_uid)):
            yield resource

    def get_by_id(self, space_guid):
        return super(SpaceManager, self)._get_one('%s/v2/spaces/%s' % (self.target_endpoint, space_guid))
