import httplib
import unittest

from abstract_test_case import AbstractTestCase
from fake_requests import mock_response


class TestBuildpacks(unittest.TestCase, AbstractTestCase):
    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = mock_response('/v2/buildpacks',
                                                     httplib.OK,
                                                     None,
                                                     'v2', 'buildpacks', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1, self.client.buildpacks.list(), 0)
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(cpt, 3)

    def test_update(self):
        self.client.put.return_value = mock_response(
            '/v2/buildpacks/build_pack_id',
            httplib.CREATED,
            None,
            'v2', 'apps', 'PUT_{id}_response.json')
        result = self.client.buildpacks.update('build_pack_id', dict(enabled=False))
        self.client.put.assert_called_with(self.client.put.return_value.url,
                                           json=dict(enabled=False))
        self.assertIsNotNone(result)
