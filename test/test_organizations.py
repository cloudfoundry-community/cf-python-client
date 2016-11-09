import sys
import unittest

import cloudfoundry_client.main as main
from abstract_test_case import AbstractTestCase
from cloudfoundry_client.imported import OK, reduce
from fake_requests import mock_response
from imported import patch, call


class TestOrganizations(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = mock_response('/v2/organizations?q=name%20IN%20organization_name',
                                                     OK,
                                                     None,
                                                     'v2', 'organizations', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1, self.client.organizations.list(name='organization_name'), 0)
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.client.get.return_value = mock_response(
            '/v2/organizations/org_id',
            OK,
            None,
            'v2', 'organizations', 'GET_{id}_response.json')
        result = self.client.organizations.get('org_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)

    def test_entity(self):
        self.client.get.side_effect = [
            mock_response(
                '/v2/organizations/org_id',
                OK,
                None,
                'v2', 'organizations', 'GET_{id}_response.json'),
            mock_response(
                '/v2/organizations/fe79371b-39b8-4f0d-8331-cff423a06aca/spaces',
                OK,
                None,
                'v2', 'spaces', 'GET_response.json')
        ]
        organization = self.client.organizations.get('org_id')
        cpt = reduce(lambda increment, _: increment + 1, organization.spaces(), 0)
        self.assertEqual(cpt, 1)
        self.client.get.assert_has_calls([call(side_effect.url) for side_effect in self.client.get.side_effect],
                                         any_order=False)

    @patch.object(sys, 'argv', ['main', 'list_organizations'])
    def test_main_list_organizations(self):
        with patch('cloudfoundry_client.main.build_client_from_configuration',
                   new=lambda: self.client):
            self.client.get.return_value = mock_response('/v2/organizations',
                                                         OK,
                                                         None,
                                                         'v2', 'organizations', 'GET_response.json')
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)

    @patch.object(sys, 'argv', ['main', 'get_organization', 'fe79371b-39b8-4f0d-8331-cff423a06aca'])
    def test_main_get_organization(self):
        with patch('cloudfoundry_client.main.build_client_from_configuration',
                   new=lambda: self.client):
            self.client.get.return_value = mock_response('/v2/organizations/fe79371b-39b8-4f0d-8331-cff423a06aca',
                                                         OK,
                                                         None,
                                                         'v2', 'organizations', 'GET_{id}_response.json')
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)
