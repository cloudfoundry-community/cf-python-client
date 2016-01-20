from cloudfoundry_client.entities import EntityManager

__author__ = 'BUCE8373'


class ServicePlanManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(ServicePlanManager, self).__init__(target_endpoint, credentials_manager, '/v2/service_plans')

    def create_from_resource_file(self, path):
        raise NotImplemented('No creation allowed')

    def list_instance(self, service_plan_guid, **kwargs):
        response = self.credentials_manager.get(
            EntityManager._get_url_filtered('%s/%s/service_instances' % (self.base_url, service_plan_guid), **kwargs))
        while True:
            for resource in response['resources']:
                yield resource
            if response['next_url'] is None:
                break
            else:
                response = self.credentials_manager.get(response['next_url'])