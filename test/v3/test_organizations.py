import unittest
from http import HTTPStatus

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.entities import Entity
from fake_requests import mock_response


class TestOrganizations(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = mock_response('/v3/organizations',
                                                     HTTPStatus.OK,
                                                     None,
                                                     'v3', 'organizations', 'GET_response.json')
        all_organizations = [organization for organization in self.client.v3.organizations.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_organizations))
        self.assertEqual(all_organizations[0]['name'], "org1")
        self.assertIsInstance(all_organizations[0], Entity)

    def test_get(self):
        self.client.get.return_value = mock_response('/v3/organizations/organization_id',
                                                     HTTPStatus.OK,
                                                     None,
                                                     'v3', 'organizations', 'GET_{id}_response.json')
        organization = self.client.v3.organizations.get('organization_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual("my-organization", organization['name'])
        self.assertIsInstance(organization, Entity)


