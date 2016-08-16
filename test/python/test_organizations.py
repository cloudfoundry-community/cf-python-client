import httplib
import unittest

import mock

from abstract_test_case import AbstractTestCase
from fake_requests import mock_response


class TestOrganizations(unittest.TestCase, AbstractTestCase):
    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = mock_response('/v2/organizations?q=name%20IN%20organization_name',
                                                     httplib.OK,
                                                     None,
                                                     'v2', 'organizations', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1, self.client.organizations.list(name='organization_name'), 0)
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.client.get.return_value = mock_response(
            '/v2/organizations/org_id',
            httplib.OK,
            None,
            'v2', 'organizations', 'GET_{id}_response.json')
        result = self.client.organizations.get('org_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)

    def test_entity(self):
        self.client.get.side_effect = [
            mock_response(
                '/v2/organizations/org_id',
                httplib.OK,
                None,
                'v2', 'organizations', 'GET_{id}_response.json'),
            mock_response(
                '/v2/organizations/fe79371b-39b8-4f0d-8331-cff423a06aca/spaces',
                httplib.OK,
                None,
                'v2', 'spaces', 'GET_response.json')
        ]
        organization = self.client.organizations.get('org_id')
        cpt = reduce(lambda increment, _: increment + 1, organization.spaces(), 0)
        self.assertEqual(cpt, 1)
        self.client.get.assert_has_calls([mock.call(side_effect.url) for side_effect in self.client.get.side_effect],
                                         any_order=False)
