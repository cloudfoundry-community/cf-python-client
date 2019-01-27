from cloudfoundry_client.v2.entities import EntityManager


class ServiceKeyManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(ServiceKeyManager, self).__init__(target_endpoint, client, '/v2/service_keys')

    def create(self, service_instance_guid, name, parameters=None):
        request = self._request(service_instance_guid=service_instance_guid, name=name)
        request['parameters'] = parameters
        return super(ServiceKeyManager, self)._create(request)

    def remove(self, key_guid):
        super(ServiceKeyManager, self)._remove(key_guid)
