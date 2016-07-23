from cloudfoundry_client.entities import EntityManager

__author__ = 'BUCE8373'


class ServicePlanManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(ServicePlanManager, self).__init__(target_endpoint, credentials_manager, '/v2/service_plans')

    def create_from_resource_file(self, path):
        raise NotImplemented('No creation allowed')

    def list_instances(self, service_plan_guid, **kwargs):
        for instance in super(ServicePlanManager, self).list(service_plan_guid, 'service_instances', **kwargs):
            yield instance
