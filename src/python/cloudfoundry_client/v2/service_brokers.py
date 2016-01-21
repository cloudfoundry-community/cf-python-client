from cloudfoundry_client.entities import EntityManager

__author__ = 'BUCE8373'


class ServiceBrokerManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(ServiceBrokerManager, self).__init__(target_endpoint, credentials_manager, '/v2/service_brokers')

    def create(self, broker_url, broker_name, auth_username, auth_password, space_guid=None):
        request = dict(broker_url=broker_url,
                       name=broker_name,
                       auth_username=auth_username,
                       auth_password=auth_password)
        if space_guid is not None:
            request['space_guid'] = space_guid
        return super(ServiceBrokerManager, self)._create(request)

    def update(self, broker_guid, broker_url, broker_name, auth_username, auth_password):
        request = dict(broker_url=broker_url,
                       name=broker_name,
                       auth_username=auth_username,
                       auth_password=auth_password)
        return super(ServiceBrokerManager, self)._update(broker_guid, request)

    def remove(self, broker_guid):
        super(ServiceBrokerManager, self)._remove(broker_guid)