import httplib
import unittest

import mock

from cloudfoundry_client.v2.services import ServiceManager
from fake_requests import mock_response, TARGET_ENDPOINT


class TestServices(unittest.TestCase):

    def setUp(self):
        self.credential_manager = mock.MagicMock()
        self.services = ServiceManager(TARGET_ENDPOINT, self.credential_manager)

    def test_list(self):
        self.credential_manager.get.return_value = mock_response('/v2/services?q=label%20IN%20some_label',
                                                                 httplib.OK,
                                                                 'v2', 'services', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1, self.services.list(label='some_label'), 0)
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.credential_manager.get.return_value = mock_response(
            '/v2/services/service_id',
            httplib.OK,
            'v2', 'services', 'GET_{id}_response.json')
        result = self.services.get('service_id')
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertIsNotNone(result)


