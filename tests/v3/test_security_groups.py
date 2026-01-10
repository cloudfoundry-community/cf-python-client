import unittest
from http import HTTPStatus

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.entities import Entity, ToManyRelationship, ToOneRelationship
from cloudfoundry_client.v3.security_groups import Rule, RuleProtocol, GloballyEnabled


class TestSecurityGroups(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_create(self):
        self.client.post.return_value = self.mock_response(
            "/v3/security_groups", HTTPStatus.CREATED, None, "v3", "security_groups", "POST_response.json"
        )
        group_name = "my-group0"
        result = self.client.v3.security_groups.create(group_name, rules=[
            Rule(protocol=RuleProtocol.TCP, destination="10.10.10.0/24", ports="443,80,8080"),
            Rule(protocol=RuleProtocol.ICMP, destination="10.10.10.0/24", type=8, code=0,
                 description="Allow ping requests to private services")])
        self.client.post.assert_called_with(
            self.client.post.return_value.url,
            json={
                "name": group_name,
                "rules": [
                    {"protocol": "tcp", "destination": "10.10.10.0/24", "ports": "443,80,8080"},
                    {"protocol": "icmp", "destination": "10.10.10.0/24", "type": 8, "code": 0,
                     "description": "Allow ping requests to private services"}
                ]
            },
            files=None
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)

    def test_list(self):
        self.client.get.return_value = self.mock_response(
            "/v3/security_groups", HTTPStatus.OK, None, "v3", "security_groups", "GET_response.json"
        )
        all_security_groups = [security_group for security_group in self.client.v3.security_groups.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_security_groups))
        self.assertEqual(all_security_groups[0]["name"], "my-group0")
        self.assertIsInstance(all_security_groups[0], Entity)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v3/security_groups/security_group_guid_123", HTTPStatus.OK, None, "v3", "security_groups",
            "GET_{id}_response.json"
        )
        security_group = self.client.v3.security_groups.get("security_group_guid_123")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual("my-group0", security_group["name"])
        self.assertIsInstance(security_group, Entity)

    def test_update(self):
        self.client.patch.return_value = self.mock_response(
            "/v3/security_groups/security_group_guid_123", HTTPStatus.OK, None, "v3", "security_groups",
            "PATCH_{id}_response.json"
        )
        group_name = "my-group0"
        result = self.client.v3.security_groups.update("security_group_guid_123",
                                                       group_name,
                                                       rules=[
                                                           Rule(protocol=RuleProtocol.TCP, destination="10.10.10.0/24",
                                                                ports="443,80,8080"),
                                                           Rule(protocol=RuleProtocol.ICMP, destination="10.10.10.0/24",
                                                                type=8, code=0,
                                                                description="Allow ping requests to private services")
                                                       ],
                                                       globally_enabled=GloballyEnabled(running=True))
        self.client.patch.assert_called_with(
            self.client.patch.return_value.url,
            json={
                "name": group_name,
                "rules": [
                    {"protocol": "tcp", "destination": "10.10.10.0/24", "ports": "443,80,8080"},
                    {"protocol": "icmp", "destination": "10.10.10.0/24", "type": 8, "code": 0,
                     "description": "Allow ping requests to private services"}
                ],
                "globally_enabled": {
                    "running": True
                }
            }
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)

    def test_remove(self):
        self.client.delete.return_value = self.mock_response("/v3/security_groups/security_group_guid",
                                                             HTTPStatus.NO_CONTENT, None)
        self.client.v3.security_groups.remove("security_group_guid")
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    def test_bind_running_spaces(self):
        self.client.post.return_value = self.mock_response(
            "/v3/security_groups/security_group_guid/relationships/running_spaces",
            HTTPStatus.OK, None, "v3", "security_groups", "POST_{id}_relationships_running_spaces_response.json"
        )
        result = self.client.v3.security_groups.bind_running_security_group_to_spaces("security_group_guid",
                                                                                      ToManyRelationship("space-guid1",
                                                                                                         "space-guid2"))

        self.client.post.assert_called_with(
            self.client.post.return_value.url,
            json={
                "data": [
                    {"guid": "space-guid1"},
                    {"guid": "space-guid2"}
                ]
            },
            files=None
        )
        self.assertIsInstance(result, ToManyRelationship)
        self.assertListEqual(["space-guid1", "space-guid2", "previous-space-guid"], result.guids)

    def test_bind_staging_spaces(self):
        self.client.post.return_value = self.mock_response(
            "/v3/security_groups/security_group_guid/relationships/staging_spaces",
            HTTPStatus.OK, None, "v3", "security_groups", "POST_{id}_relationships_staging_spaces_response.json"
        )
        result = self.client.v3.security_groups.bind_staging_security_group_to_spaces("security_group_guid",
                                                                                      ToManyRelationship("space-guid1",
                                                                                                         "space-guid2"))

        self.client.post.assert_called_with(
            self.client.post.return_value.url,
            json={
                "data": [
                    {"guid": "space-guid1"},
                    {"guid": "space-guid2"}
                ]
            },
            files=None
        )
        self.assertIsInstance(result, ToManyRelationship)
        self.assertListEqual(["space-guid1", "space-guid2", "previous-space-guid"], result.guids)

    def test_unbind_running_from_space(self):
        self.client.delete.return_value = self.mock_response(
            "/v3/security_groups/security_group_guid/relationships/running_spaces/space-guid",
            HTTPStatus.NO_CONTENT, None)
        self.client.v3.security_groups.unbind_running_security_group_from_space("security_group_guid",
                                                                                ToOneRelationship("space-guid"))

        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    def test_unbind_staging_from_space(self):
        self.client.delete.return_value = self.mock_response(
            "/v3/security_groups/security_group_guid/relationships/staging_spaces/space-guid",
            HTTPStatus.NO_CONTENT, None)
        self.client.v3.security_groups.unbind_staging_security_group_from_space("security_group_guid",
                                                                                ToOneRelationship("space-guid"))

        self.client.delete.assert_called_with(self.client.delete.return_value.url)
