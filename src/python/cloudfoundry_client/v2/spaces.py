from cloudfoundry_client.entities import Entity, EntityManager


class _Space(Entity):
    def __init__(self, space_manager, *args, **kwargs):
        super(_Space, self).__init__(space_manager, *args, **kwargs)

    def organization(self):
        return self.client.organization._get(self.entity.organization_url)

    def applications(self, **kwargs):
        return self.client.application._list(self.entity.apps_url, **kwargs)

    def service_instances(self, **kwargs):
        return self.client.service_instance._list(self.entity.service_instances_url, **kwargs)


class SpaceManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(SpaceManager, self).__init__(target_endpoint, client, '/v2/spaces',
                                           lambda pairs: _Space(client, pairs))
