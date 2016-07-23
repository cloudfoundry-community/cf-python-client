import httplib
import unittest

import mock

from cloudfoundry_client.v2.service_bindings import ServiceBindingManager
from fake_requests import mock_response, TARGET_ENDPOINT


class TestServiceBindings(unittest.TestCase):
    def setUp(self):
        self.credential_manager = mock.MagicMock()
        self.service_bindings = ServiceBindingManager(TARGET_ENDPOINT, self.credential_manager)

    def test_list(self):
        self.credential_manager.get.return_value = mock_response(
            '/v2/service_bindings?q=service_instance_guid%20IN%20instance_guid',
            httplib.OK,
            'v2', 'service_bindings', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1,
                     self.service_bindings.list(service_instance_guid='instance_guid'), 0)
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.credential_manager.get.return_value = mock_response(
            '/v2/service_bindings/route_id',
            httplib.OK,
            'v2', 'service_bindings', 'GET_{id}_response.json')
        result = self.service_bindings.get('route_id')
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertIsNotNone(result)

    def test_create(self):
        self.credential_manager.post.return_value = mock_response(
            '/v2/service_bindings',
            httplib.CREATED,
            'v2', 'service_bindings', 'POST_response.json')
        service_bindiing = self.service_bindings.create('app_guid', 'instance_guid',
                                                        dict(the_service_broker='wants this object'))
        self.credential_manager.post.assert_called_with(self.credential_manager.post.return_value.url,
                                                        json=dict(app_guid='app_guid',
                                                                  service_instance_guid='instance_guid',
                                                                  parameters=dict(
                                                                      the_service_broker='wants this object')))
        self.assertIsNotNone(service_bindiing)

    def test_delete(self):
        self.credential_manager.delete.return_value = mock_response(
            '/v2/service_bindings/binding_id',
            httplib.NO_CONTENT)
        self.service_bindings.remove('binding_id')
        self.credential_manager.delete.assert_called_with(self.credential_manager.delete.return_value.url)