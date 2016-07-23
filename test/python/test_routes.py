import httplib
import unittest

import mock

from cloudfoundry_client.v2.routes import RouteManager
from fake_requests import mock_response, TARGET_ENDPOINT


class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.credential_manager = mock.MagicMock()
        self.routes = RouteManager(TARGET_ENDPOINT, self.credential_manager)

    def test_list(self):
        self.credential_manager.get.return_value = mock_response(
            '/v2/routes?q=organization_guid%20IN%20organization_guid',
            httplib.OK,
            None,
            'v2', 'routes', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1, self.routes.list(organization_guid='organization_guid'), 0)
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.credential_manager.get.return_value = mock_response(
            '/v2/routes/route_id',
            httplib.OK,
            None,
            'v2', 'routes', 'GET_{id}_response.json')
        result = self.routes.get('route_id')
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertIsNotNone(result)
