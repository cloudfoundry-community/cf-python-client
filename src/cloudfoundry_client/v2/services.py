from cloudfoundry_client.entities import EntityManager


class ServiceManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(ServiceManager, self).__init__(target_endpoint, credentials_manager, '/v2/services')


class ServicePlanManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(ServicePlanManager, self).__init__(target_endpoint, credentials_manager, '/v2/service_plans')


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

    def remove(self, instance_guid):
        super(ServiceInstanceManager, self)._remove(instance_guid)


class ServiceBindingManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(ServiceBindingManager, self).__init__(target_endpoint, credentials_manager, '/v2/service_bindings')

    def create(self, app_guid, instance_guid, parameters=None):
        request = dict(app_guid=app_guid,
                       service_instance_guid=instance_guid)
        if parameters is None:
            request['parameters'] = {}
        else:
            request['parameters'] = parameters
        return super(ServiceBindingManager, self)._create(request)

    def remove(self, binding_id):
        super(ServiceBindingManager, self)._remove(binding_id)




