import sys
import unittest

import cloudfoundry_client.main as main
from abstract_test_case import AbstractTestCase
from cloudfoundry_client.imported import OK, reduce
from fake_requests import mock_response
from imported import patch, call


class TestRoutes(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = mock_response(
            '/v2/routes?q=organization_guid%20IN%20organization_guid',
            OK,
            None,
            'v2', 'routes', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1, self.client.routes.list(organization_guid='organization_guid'),
                     0)
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.client.get.return_value = mock_response(
            '/v2/routes/route_id',
            OK,
            None,
            'v2', 'routes', 'GET_{id}_response.json')
        result = self.client.routes.get('route_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)

    def test_entity(self):
        self.client.get.side_effect = [
            mock_response(
                '/v2/routes/route_id',
                OK,
                None,
                'v2', 'routes', 'GET_{id}_response.json'),
            mock_response(
                '/v2/service_instances/e3db4ea8-ab0c-4c47-adf8-a70a8e990ee4',
                OK,
                None,
                'v2', 'service_instances', 'GET_{id}_response.json'),
            mock_response(
                '/v2/spaces/b3f94ab9-1520-478b-a6d6-eb467c179ada',
                OK,
                None,
                'v2', 'spaces', 'GET_{id}_response.json'),
            mock_response('/v2/routes/75c16cfe-9b8a-4faf-bb65-02c713c7956f/apps',
                          OK,
                          None,
                          'v2', 'apps', 'GET_response.json')
        ]
        route = self.client.routes.get('route_id')
        self.assertIsNotNone(route.service_instance())
        self.assertIsNotNone(route.space())
        cpt = reduce(lambda increment, _: increment + 1, route.apps(), 0)
        self.assertEqual(cpt, 3)
        self.client.get.assert_has_calls([call(side_effect.url) for side_effect in self.client.get.side_effect],
                                         any_order=False)

    @patch.object(sys, 'argv', ['main', 'list_routes'])
    def test_main_list_routes(self):
        with patch('cloudfoundry_client.main.build_client_from_configuration',
                   new=lambda: self.client):
            self.client.get.return_value = mock_response('/v2/routes',
                                                         OK,
                                                         None,
                                                         'v2', 'routes', 'GET_response.json')
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)

    @patch.object(sys, 'argv', ['main', 'get_route', '75c16cfe-9b8a-4faf-bb65-02c713c7956f'])
    def test_main_get_route(self):
        with patch('cloudfoundry_client.main.build_client_from_configuration',
                   new=lambda: self.client):
            self.client.get.return_value = mock_response('/v2/routes/75c16cfe-9b8a-4faf-bb65-02c713c7956f',
                                                         OK,
                                                         None,
                                                         'v2', 'routes', 'GET_{id}_response.json')
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)
