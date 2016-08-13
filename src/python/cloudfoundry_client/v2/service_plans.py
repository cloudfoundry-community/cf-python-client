from cloudfoundry_client.entities import Entity, EntityManager


class _ServicePlan(Entity):
    def service(self):
        return self.client.service._get(self.entity.service_url)

    def service_instances(self, **kwargs):
        return self.client.service_instance._list(self.entity.service_instances_url, **kwargs)
        

class ServicePlanManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(ServicePlanManager, self).__init__(target_endpoint, client, '/v2/service_plans',
                                                 lambda pairs: _ServicePlan(client, pairs))

    def create_from_resource_file(self, path):
        raise NotImplementedError('No creation allowed')

    def list_instances(self, service_plan_guid, **kwargs):
        return self.client.service_instance._list('%s/%s/service_instances' % (self.entity_uri, service_plan_guid),
                                                  **kwargs)
