import unittest

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.imported import OK, reduce
from cloudfoundry_client.v3.entities import Entity
from fake_requests import mock_response
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

    def test_remove(self):
        self.client.delete.return_value = mock_response(
            '/v3/buildpacks/buildpack_id',
            NO_CONTENT,
            None)
        self.client.v3.buildpacks.remove('buildpack_id')
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

