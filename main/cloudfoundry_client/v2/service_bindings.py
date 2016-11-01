from cloudfoundry_client.entities import EntityManager


class ServiceBindingManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(ServiceBindingManager, self).__init__(target_endpoint, client, '/v2/service_bindings')

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
