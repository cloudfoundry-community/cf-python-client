import unittest
from http import HTTPStatus

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.entities import Entity


class TestRoles(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = self.mock_response("/v3/roles", HTTPStatus.OK, None, "v3", "roles",
                                                          "GET_response.json")
        all_roles = [role for role in self.client.v3.roles.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_roles))
        self.assertEqual(all_roles[0]["type"], "organization_auditor")
        self.assertIsInstance(all_roles[0], Entity)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v3/roles/role_id", HTTPStatus.OK, None, "v3", "roles", "GET_{id}_response.json"
        )
        role = self.client.v3.roles.get("role_id")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(role["type"], "organization_auditor")
        self.assertIsInstance(role, Entity)

    def test_remove(self):
        self.client.delete.return_value = self.mock_response("/v3/roles/role_id", HTTPStatus.NO_CONTENT, None)
        self.client.v3.roles.remove("role_id")
        self.client.delete.assert_called_with(self.client.delete.return_value.url)
