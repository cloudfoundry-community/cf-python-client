from cloudfoundry_client.entities import Entity, EntityManager


class _Route(Entity):
    def applications(self, **kwargs):
        return self.client.application._list(self.entity.apps_url, **kwargs)

    def space(self):
        return self.client.space._get(self.entity.space_url)

    def service_instance(self):
        return self.client.service_instance._get(self.entity.service_instance_url)


class RouteManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(RouteManager, self).__init__(target_endpoint, client, '/v2/routes',
                                           lambda pairs: _Route(client, pairs))
