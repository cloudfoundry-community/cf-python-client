from cloudfoundry_client.entities import EntityManager


class ServicePlanManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(ServicePlanManager, self).__init__(target_endpoint, client, '/v2/service_plans')

    def create_from_resource_file(self, path):
        raise NotImplementedError('No creation allowed')

    def list_instances(self, service_plan_guid, **kwargs):
        return self.client.service_instances._list('%s/%s/service_instances' % (self.entity_uri, service_plan_guid),
                                                  **kwargs)
