import unittest
from http import HTTPStatus

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.entities import Entity


class TestUsers(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_create(self):
        self.client.post.return_value = self.mock_response(
            "/v3/users", HTTPStatus.OK, None, "v3", "users", "POST_response.json"
        )
        result = self.client.v3.users.create("3a5d3d89-3f89-4f05-8188-8a2b298c79d5")
        self.client.post.assert_called_with(
            self.client.post.return_value.url,
            files=None,
            json={"guid": "3a5d3d89-3f89-4f05-8188-8a2b298c79d5"},
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)

    def test_list(self):
        self.client.get.return_value = self.mock_response(
            "/v3/users", HTTPStatus.OK, None, "v3", "users", "GET_response.json"
        )
        all_users = [user for user in self.client.v3.users.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_users))
        self.assertEqual(all_users[0]["guid"], "client_id")
        self.assertIsInstance(all_users[0], Entity)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v3/users/user_id", HTTPStatus.OK, None, "v3", "users", "GET_{id}_response.json"
        )
        user = self.client.v3.users.get("user_id")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual("uaa", user["origin"])
        self.assertIsInstance(user, Entity)

    def test_update(self):
        self.client.patch.return_value = self.mock_response(
            "/v3/users/user_id", HTTPStatus.OK, None, "v3", "users", "PATCH_{id}_response.json"
        )
        result = self.client.v3.users.update(
            "user_id",
            {"environment": "production"},
            {"note": "detailed information"}
        )

        self.client.patch.assert_called_with(
            self.client.patch.return_value.url,
            json={
                "metadata": {
                    "labels": {"environment": "production"},
                    "annotations": {"note": "detailed information"}
                }
            },
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)

    def test_remove(self):
        self.client.delete.return_value = self.mock_response("/v3/users/user_id", HTTPStatus.NO_CONTENT, None)
        self.client.v3.users.remove("user_id")
        self.client.delete.assert_called_with(self.client.delete.return_value.url)
