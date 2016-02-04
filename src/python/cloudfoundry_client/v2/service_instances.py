from cloudfoundry_client.entities import EntityManager

__author__ = 'BUCE8373'


class ServiceInstanceManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(ServiceInstanceManager, self).__init__(target_endpoint, credentials_manager, '/v2/service_instances')

    def create(self, space_guid, instance_name, plan_guid, parameters):
        request = dict(name=instance_name,
                       space_guid=space_guid,
                       service_plan_guid=plan_guid,
                       parameters=parameters)
        return super(ServiceInstanceManager, self)._create(request)

    def update(self, instance_guid, parameters):
        request = dict(parameters=parameters, tags=[])
        return super(ServiceInstanceManager, self)._update(instance_guid, request)

    def list_permissions(self, instance_guid):
        return super(ServiceInstanceManager, self)._get_one('%s/%s/permissions' % (self.base_url, instance_guid))

    def remove(self, instance_guid):
        super(ServiceInstanceManager, self)._remove(instance_guid)