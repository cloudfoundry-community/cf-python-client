import sys
import unittest

import cloudfoundry_client.main as main
from abstract_test_case import AbstractTestCase
from cloudfoundry_client.imported import OK, reduce
from fake_requests import mock_response
from imported import CREATED, patch


class TestBuildpacks(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = mock_response('/v2/buildpacks',
                                                     OK,
                                                     None,
                                                     'v2', 'buildpacks', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1, self.client.buildpacks.list(), 0)
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(cpt, 3)

    def test_get(self):
        self.client.get.return_value = mock_response(
            '/v2/buildpacks/buildpack_id',
            OK,
            None,
            'v2', 'buildpacks', 'GET_{id}_response.json')
        result = self.client.buildpacks.get('buildpack_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)

    def test_update(self):
        self.client.put.return_value = mock_response(
            '/v2/buildpacks/build_pack_id',
            CREATED,
            None,
            'v2', 'apps', 'PUT_{id}_response.json')
        result = self.client.buildpacks.update('build_pack_id', dict(enabled=False))
        self.client.put.assert_called_with(self.client.put.return_value.url,
                                           json=dict(enabled=False))
        self.assertIsNotNone(result)

    @patch.object(sys, 'argv', ['main', 'list_buildpacks'])
    def test_main_list_buildpacks(self):
        with patch('cloudfoundry_client.main.build_client_from_configuration',
                        new=lambda: self.client):
            self.client.get.return_value = mock_response('/v2/buildpacks',
                                                         OK,
                                                         None,
                                                         'v2', 'buildpacks', 'GET_response.json')
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)

    @patch.object(sys, 'argv', ['main', 'get_buildpack', '6e72c33b-dff0-4020-8603-bcd8a4eb05e4'])
    def test_main_get_buildpack(self):
        with patch('cloudfoundry_client.main.build_client_from_configuration',
                        new=lambda: self.client):
            self.client.get.return_value = mock_response('/v2/buildpacks/6e72c33b-dff0-4020-8603-bcd8a4eb05e4',
                                                         OK,
                                                         None,
                                                         'v2', 'buildpacks', 'GET_{id}_response.json')
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)
