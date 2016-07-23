import httplib
import unittest

import mock

from cloudfoundry_client.v2.service_brokers import ServiceBrokerManager
from fake_requests import mock_response, TARGET_ENDPOINT


class TestServiceBrokers(unittest.TestCase):
    def setUp(self):
        self.credential_manager = mock.MagicMock()
        self.service_brokers = ServiceBrokerManager(TARGET_ENDPOINT, self.credential_manager)

    def test_list(self):
        self.credential_manager.get.return_value = mock_response(
            '/v2/service_brokers?q=space_guid%20IN%20space_guid',
            httplib.OK,
            None,
            'v2', 'service_bindings', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1,
                     self.service_brokers.list(space_guid='space_guid'), 0)
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.credential_manager.get.return_value = mock_response(
            '/v2/service_brokers/broker_id',
            httplib.OK,
            None,
            'v2', 'service_brokers', 'GET_{id}_response.json')
        result = self.service_brokers.get('broker_id')
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertIsNotNone(result)

    def test_create(self):
        self.credential_manager.post.return_value = mock_response(
            '/v2/service_brokers',
            httplib.CREATED,
            None,
            'v2', 'service_brokers', 'POST_response.json')
        service_broker = self.service_brokers.create('url', 'name', 'username', 'P@sswd1')
        self.credential_manager.post.assert_called_with(self.credential_manager.post.return_value.url,
                                                        json=dict(broker_url='url',
                                                                  name='name',
                                                                  auth_username='username',
                                                                  auth_password='P@sswd1'))
        self.assertIsNotNone(service_broker)

    def test_update(self):
        self.credential_manager.put.return_value = mock_response(
            '/v2/service_brokers/broker_id',
            httplib.OK,
            None,
            'v2', 'service_brokers', 'PUT_{id}_response.json')
        service_broker = self.service_brokers.update('broker_id',
                                                     broker_url='new-url',
                                                     auth_username='new-username',
                                                     auth_password='P@sswd2')
        self.credential_manager.put.assert_called_with(self.credential_manager.put.return_value.url,
                                                       json=dict(broker_url='new-url',
                                                                 auth_username='new-username',
                                                                 auth_password='P@sswd2'))
        self.assertIsNotNone(service_broker)

    def test_delete(self):
        self.credential_manager.delete.return_value = mock_response(
            '/v2/service_brokers/broker_id',
            httplib.NO_CONTENT,
            None)
        self.service_brokers.remove('broker_id')
        self.credential_manager.delete.assert_called_with(self.credential_manager.delete.return_value.url)
