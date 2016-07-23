import httplib
import unittest

import mock

from cloudfoundry_client.v2.spaces import SpaceManager
from fake_requests import mock_response, TARGET_ENDPOINT


class TestSpaces(unittest.TestCase):

    def setUp(self):
        self.credential_manager = mock.MagicMock()
        self.spaces = SpaceManager(TARGET_ENDPOINT, self.credential_manager)

    def test_list(self):
        self.credential_manager.get.return_value = mock_response('/v2/spaces?q=organization_guid%20IN%20org_id',
                                                                 httplib.OK,
                                                                 'v2', 'spaces', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1, self.spaces.list(organization_guid='org_id'), 0)
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.credential_manager.get.return_value = mock_response(
            '/v2/spaces/space_id',
            httplib.OK,
            'v2', 'spaces', 'GET_{id}_response.json')
        result = self.spaces.get('space_id')
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertIsNotNone(result)


