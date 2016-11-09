import sys
import unittest

import cloudfoundry_client.main as main
from abstract_test_case import AbstractTestCase
from cloudfoundry_client.imported import OK, reduce
from fake_requests import mock_response
from imported import patch, call


class TestSpaces(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = mock_response('/v2/spaces?q=organization_guid%20IN%20org_id',
                                                     OK,
                                                     None,
                                                     'v2', 'spaces', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1, self.client.spaces.list(organization_guid='org_id'), 0)
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.client.get.return_value = mock_response(
            '/v2/spaces/space_id',
            OK,
            None,
            'v2', 'spaces', 'GET_{id}_response.json')
        result = self.client.spaces.get('space_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)

    def test_entity(self):
        self.client.get.side_effect = [
            mock_response(
                '/v2/spaces/space_id',
                OK,
                None,
                'v2', 'spaces', 'GET_{id}_response.json'),
            mock_response(
                '/v2/organizations/d7d77408-a250-45e3-8de5-71fcf199bbab',
                OK,
                None,
                'v2', 'organizations', 'GET_{id}_response.json'),
            mock_response(
                '/v2/spaces/2d745a4b-67e3-4398-986e-2adbcf8f7ec9/apps',
                OK,
                None,
                'v2', 'apps', 'GET_response.json'),
            mock_response(
                '/v2/spaces/2d745a4b-67e3-4398-986e-2adbcf8f7ec9/service_instances',
                OK,
                None,
                'v2', 'service_instances', 'GET_response.json')
        ]
        space = self.client.spaces.get('space_id')
        self.assertIsNotNone(space.organization())
        cpt = reduce(lambda increment, _: increment + 1, space.apps(), 0)
        self.assertEqual(cpt, 3)
        cpt = reduce(lambda increment, _: increment + 1, space.service_instances(), 0)
        self.assertEqual(cpt, 1)
        self.client.get.assert_has_calls([call(side_effect.url) for side_effect in self.client.get.side_effect],
                                         any_order=False)

    @patch.object(sys, 'argv', ['main', 'list_spaces'])
    def test_main_list_spaces(self):
        with patch('cloudfoundry_client.main.build_client_from_configuration',
                   new=lambda: self.client):
            self.client.get.return_value = mock_response('/v2/spaces',
                                                         OK,
                                                         None,
                                                         'v2', 'spaces', 'GET_response.json')
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)

    @patch.object(sys, 'argv', ['main', 'get_space', '2d745a4b-67e3-4398-986e-2adbcf8f7ec9'])
    def test_main_get_spaces(self):
        with patch('cloudfoundry_client.main.build_client_from_configuration',
                   new=lambda: self.client):
            self.client.get.return_value = mock_response('/v2/spaces/2d745a4b-67e3-4398-986e-2adbcf8f7ec9',
                                                         OK,
                                                         None,
                                                         'v2', 'spaces', 'GET_{id}_response.json')
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)
