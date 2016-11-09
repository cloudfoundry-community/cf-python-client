import sys
import unittest

import cloudfoundry_client.main as main
from abstract_test_case import AbstractTestCase
from cloudfoundry_client.imported import OK, reduce
from fake_requests import mock_response
from imported import patch, CREATED, NO_CONTENT


class TestServiceBrokers(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = mock_response(
            '/v2/service_brokers?q=space_guid%20IN%20space_guid',
            OK,
            None,
            'v2', 'service_bindings', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1,
                     self.client.service_brokers.list(space_guid='space_guid'), 0)
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.client.get.return_value = mock_response(
            '/v2/service_brokers/broker_id',
            OK,
            None,
            'v2', 'service_brokers', 'GET_{id}_response.json')
        result = self.client.service_brokers.get('broker_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)

    def test_create(self):
        self.client.post.return_value = mock_response(
            '/v2/service_brokers',
            CREATED,
            None,
            'v2', 'service_brokers', 'POST_response.json')
        service_broker = self.client.service_brokers.create('url', 'name', 'username', 'P@sswd1')
        self.client.post.assert_called_with(self.client.post.return_value.url,
                                            json=dict(broker_url='url',
                                                      name='name',
                                                      auth_username='username',
                                                      auth_password='P@sswd1'))
        self.assertIsNotNone(service_broker)

    def test_update(self):
        self.client.put.return_value = mock_response(
            '/v2/service_brokers/broker_id',
            OK,
            None,
            'v2', 'service_brokers', 'PUT_{id}_response.json')
        service_broker = self.client.service_brokers.update('broker_id',
                                                            broker_url='new-url',
                                                            auth_username='new-username',
                                                            auth_password='P@sswd2')
        self.client.put.assert_called_with(self.client.put.return_value.url,
                                           json=dict(broker_url='new-url',
                                                     auth_username='new-username',
                                                     auth_password='P@sswd2'))
        self.assertIsNotNone(service_broker)

    def test_delete(self):
        self.client.delete.return_value = mock_response(
            '/v2/service_brokers/broker_id',
            NO_CONTENT,
            None)
        self.client.service_brokers.remove('broker_id')
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    @patch.object(sys, 'argv', ['main', 'list_service_brokers'])
    def test_main_list_service_brokers(self):
        with patch('cloudfoundry_client.main.build_client_from_configuration',
                        new=lambda: self.client):
            self.client.get.return_value = mock_response('/v2/service_brokers',
                                                         OK,
                                                         None,
                                                         'v2', 'service_brokers', 'GET_response.json')
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)

    @patch.object(sys, 'argv', ['main', 'get_service_broker', 'ade9730c-4ee5-4290-ad37-0b15cecd2ca6'])
    def test_main_get_service_broker(self):
        with patch('cloudfoundry_client.main.build_client_from_configuration',
                        new=lambda: self.client):
            self.client.get.return_value = mock_response('/v2/service_brokers/ade9730c-4ee5-4290-ad37-0b15cecd2ca6',
                                                         OK,
                                                         None,
                                                         'v2', 'service_brokers', 'GET_{id}_response.json')
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)
