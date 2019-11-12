import sys
import unittest

import cloudfoundry_client.main.main as main
from abstract_test_case import AbstractTestCase
from cloudfoundry_client.imported import OK, reduce
from cloudfoundry_client.v3.entities import Entity
from fake_requests import mock_response
from imported import CREATED, patch
from imported import call, NO_CONTENT


class TestBuildpacks(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = mock_response('/v3/buildpacks',
                                                     OK,
                                                     None,
                                                     'v3', 'buildpacks', 'GET_response.json')
        all_buildpacks = [buildpack for buildpack in self.client.v3.buildpacks.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(1, len(all_buildpacks))
        self.assertEqual(all_buildpacks[0]['name'], "my-buildpack")
        self.assertIsInstance(all_buildpacks[0], Entity)

    def test_get(self):
        self.client.get.return_value = mock_response(
            '/v3/buildpacks/buildpack_id',
            OK,
            None,
            'v3', 'buildpacks', 'GET_{id}_response.json')
        result = self.client.v3.buildpacks.get('buildpack_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)

    def test_update(self):
        self.client.patch.return_value = mock_response(
            '/v3/buildpacks/buildpack_id',
            OK,
            None,
            'v3', 'buildpacks', 'PATCH_{id}_response.json')
        result = self.client.v3.buildpacks.update('buildpack_id', 'ruby_buildpack',
                                                  enabled=True,
                                                  position=42,
                                                  stack='windows64')
        print(result)
        self.client.patch.assert_called_with(self.client.patch.return_value.url,
                                             json={'locked': False,
                                                   'name': 'ruby_buildpack',
                                                   'enabled': True,
                                                   'position': 42,
                                                   'stack': 'windows64',
                                                   'metadata': {
                                                       'labels': None,
                                                       'annotations': None
                                                   }
                                             })
        self.assertIsNotNone(result)

    def test_remove(self):
        self.client.delete.return_value = mock_response(
            '/v3/buildpacks/buildpack_id',
            NO_CONTENT,
            None)
        self.client.v3.buildpacks.remove('buildpack_id')
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    @patch.object(sys, 'argv', ['main', 'list_buildpacks'])
    def test_main_list_buildpacks(self):
        with patch('cloudfoundry_client.main.main.build_client_from_configuration',
                   new=lambda: self.client):
            self.client.get.return_value = mock_response('/v3/buildpacks',
                                                         OK,
                                                         None,
                                                         'v3', 'buildpacks', 'GET_response.json')
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)

    @patch.object(sys, 'argv', ['main', 'get_buildpack', '6e72c33b-dff0-4020-8603-bcd8a4eb05e4'])
    def test_main_get_buildpack(self):
        with patch('cloudfoundry_client.main.main.build_client_from_configuration',
                        new=lambda: self.client):
            self.client.get.return_value = mock_response('/v3/buildpacks/6e72c33b-dff0-4020-8603-bcd8a4eb05e4',
                                                         OK,
                                                         None,
                                                         'v3', 'buildpacks', 'GET_{id}_response.json')
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)
