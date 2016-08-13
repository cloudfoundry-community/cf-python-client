from cloudfoundry_client.entities import Entity, EntityManager


class _Organization(Entity):
    def spaces(self, **kwargs):
        return self.client.space._list(self.entity.spaces_url, **kwargs)


class OrganizationManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(OrganizationManager, self).__init__(target_endpoint, client, '/v2/organizations',
                                                  lambda pairs: _Organization(client, pairs))
