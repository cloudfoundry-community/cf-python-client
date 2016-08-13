from cloudfoundry_client.entities import Entity, EntityManager


class _Service(Entity):
    def service_plans(self, **kwargs):
        return self.client.service_plan._list(self.entity.service_plans_url, **kwargs)


class ServiceManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(ServiceManager, self).__init__(target_endpoint, client, '/v2/services',
                                             lambda pairs: _Service(client, pairs))
