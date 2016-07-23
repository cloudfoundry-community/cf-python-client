import httplib
import unittest

import mock

from cloudfoundry_client.v2.organizations import OrganizationManager
from fake_requests import mock_response, TARGET_ENDPOINT


class TestOrganizations(unittest.TestCase):

    def setUp(self):
        self.credential_manager = mock.MagicMock()
        self.organizations = OrganizationManager(TARGET_ENDPOINT, self.credential_manager)

    def test_list(self):
        self.credential_manager.get.return_value = mock_response('/v2/organizations?q=name%20IN%20organization_name',
                                                                 httplib.OK,
                                                                 None,
                                                                 'v2', 'organizations', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1, self.organizations.list(name='organization_name'), 0)
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.credential_manager.get.return_value = mock_response(
            '/v2/organizations/org_id',
            httplib.OK,
            None,
            'v2', 'organizations', 'GET_{id}_response.json')
        result = self.organizations.get('org_id')
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertIsNotNone(result)


