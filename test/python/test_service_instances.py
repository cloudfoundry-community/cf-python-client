import httplib
import unittest

import mock

from cloudfoundry_client.v2.service_instances import ServiceInstanceManager
from fake_requests import mock_response, TARGET_ENDPOINT


class TestServiceInstances(unittest.TestCase):
    def setUp(self):
        self.credential_manager = mock.MagicMock()
        self.service_instances = ServiceInstanceManager(TARGET_ENDPOINT, self.credential_manager)

    def test_list(self):
        self.credential_manager.get.return_value = mock_response(
            '/v2/service_instances?q=space_guid%20IN%20space_guid&q=service_plan_guid%20IN%20plan_id',
            httplib.OK,
            None,
            'v2', 'service_instances', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1,
                     self.service_instances.list(space_guid='space_guid', service_plan_guid='plan_id'), 0)
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.credential_manager.get.return_value = mock_response(
            '/v2/service_instances/instance_id',
            httplib.OK,
            None,
            'v2', 'service_instances', 'GET_{id}_response.json')
        result = self.service_instances.get('instance_id')
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertIsNotNone(result)

    def test_create(self):
        self.credential_manager.post.return_value = mock_response(
            '/v2/service_instances',
            httplib.CREATED,
            None,
            'v2', 'service_instances', 'POST_response.json')
        service_instance = self.service_instances.create('space_guid', 'name', 'plan_id',
                                                         parameters=dict(the_service_broker="wants this object"),
                                                         tags=['mongodb'])
        self.credential_manager.post.assert_called_with(self.credential_manager.post.return_value.url,
                                                        json=dict(name='name',
                                                                  space_guid='space_guid',
                                                                  service_plan_guid='plan_id',
                                                                  parameters=dict(
                                                                      the_service_broker="wants this object"),
                                                                  tags=['mongodb'])
                                                        )
        self.assertIsNotNone(service_instance)

    def test_update(self):
        self.credential_manager.put.return_value = mock_response(
            '/v2/service_instances/instance_id',
            httplib.OK,
            None,
            'v2', 'service_instances', 'PUT_{id}_response.json')
        service_instance = self.service_instances.update('instance_id', instance_name='new-name', tags=['other-tag'])
        self.credential_manager.put.assert_called_with(self.credential_manager.put.return_value.url,
                                                       json=dict(name='new-name',
                                                                 tags=['other-tag']))
        self.assertIsNotNone(service_instance)

    def test_delete(self):
        self.credential_manager.delete.return_value = mock_response(
            '/v2/service_instances/instance_id',
            httplib.NO_CONTENT,
            None)
        self.service_instances.remove('instance_id')
        self.credential_manager.delete.assert_called_with(self.credential_manager.delete.return_value.url)
