import unittest
from http import HTTPStatus

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.entities import Entity


class TestServiceInstances(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = self.mock_response('/v3/service_instances',
                                                          HTTPStatus.OK,
                                                          None,
                                                          'v3', 'service_instances', 'GET_response.json')
        all_service_instances = [service_instance for service_instance in self.client.v3.service_instances.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(1, len(all_service_instances))
        self.assertEqual(all_service_instances[0]['guid'], "85ccdcad-d725-4109-bca4-fd6ba062b5c8")
        self.assertIsInstance(all_service_instances[0], Entity)

    def test_get(self):
        self.client.get.return_value = self.mock_response('/v3/service_instances/service_instance_id',
                                                          HTTPStatus.OK,
                                                          None,
                                                          'v3', 'service_instances', 'GET_{id}_response.json')
        service_instance = self.client.v3.service_instances.get('service_instance_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual("85ccdcad-d725-4109-bca4-fd6ba062b5c8", service_instance['guid'])
        self.assertIsInstance(service_instance, Entity)
