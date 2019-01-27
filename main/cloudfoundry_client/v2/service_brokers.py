from cloudfoundry_client.v2.entities import EntityManager


class ServiceBrokerManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(ServiceBrokerManager, self).__init__(target_endpoint, client, '/v2/service_brokers')

    def create(self, broker_url, broker_name, auth_username, auth_password, space_guid=None):
        request = self._request(broker_url=broker_url, name=broker_name,
                                auth_username=auth_username, auth_password=auth_password)
        request['space_guid'] = space_guid
        return super(ServiceBrokerManager, self)._create(request)

    def update(self, broker_guid, broker_url=None, broker_name=None, auth_username=None, auth_password=None):
        request = self._request()
        request['broker_url'] = broker_url
        request['name'] = broker_name
        request['auth_username'] = auth_username
        request['auth_password'] = auth_password
        return super(ServiceBrokerManager, self)._update(broker_guid, request)

    def remove(self, broker_guid):
        super(ServiceBrokerManager, self)._remove(broker_guid)
