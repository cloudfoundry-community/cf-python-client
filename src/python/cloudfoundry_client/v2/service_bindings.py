from cloudfoundry_client.entities import Entity, EntityManager


class _ServiceBinding(Entity):
    def application(self):
        return self.client.application._get(self.entity.app_url)

    def service_instance(self):
        return self.client.service_instance._get(self.entity.service_instance_url)


class ServiceBindingManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(ServiceBindingManager, self).__init__(target_endpoint, client, '/v2/service_bindings',
                                                    lambda pairs: _ServiceBinding(client, pairs))

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
