import httplib
import unittest

import mock

from cloudfoundry_client.v2.buildpacks import BuildpackManager
from fake_requests import mock_response, TARGET_ENDPOINT


class TestBuildpacks(unittest.TestCase):
    def setUp(self):
        self.credential_manager = mock.MagicMock()
        self.buildpacks = BuildpackManager(TARGET_ENDPOINT, self.credential_manager)

    def test_list(self):
        self.credential_manager.get.return_value = mock_response('/v2/buildpacks',
                                                                 httplib.OK,
                                                                 'v2', 'buildpacks', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1, self.buildpacks.list(), 0)
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertEqual(cpt, 3)

    def test_update(self):
        self.credential_manager.put.return_value = mock_response(
            '/v2/buildpacks/build_pack_id',
            httplib.CREATED,
            'v2', 'apps', 'PUT_{id}_response.json')
        result = self.buildpacks.update('build_pack_id', dict(enabled=False))
        self.credential_manager.put.assert_called_with(self.credential_manager.put.return_value.url,
                                                       json=dict(enabled=False))
        self.assertIsNotNone(result)
