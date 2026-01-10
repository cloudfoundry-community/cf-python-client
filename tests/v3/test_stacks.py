import unittest
from http import HTTPStatus

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.entities import Entity


class TestStacks(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_create(self):
        self.client.post.return_value = self.mock_response(
            "/v3/stacks", HTTPStatus.CREATED, None, "v3", "stacks", "POST_response.json"
        )
        result = self.client.v3.stacks.create("my-stack", "Here is my stack!")
        self.client.post.assert_called_with(
            self.client.post.return_value.url,
            json={
                "name": "my-stack",
                "description": "Here is my stack!",
            },
            files=None
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)

    def test_list(self):
        self.client.get.return_value = self.mock_response(
            "/v3/stacks", HTTPStatus.OK, None, "v3", "stacks", "GET_response.json"
        )
        all_stacks = [stack for stack in self.client.v3.stacks.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_stacks))
        self.assertEqual(all_stacks[0]["name"], "my-stack-1")
        self.assertIsInstance(all_stacks[0], Entity)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v3/stacks/stack-id", HTTPStatus.OK, None, "v3", "stacks",
            "GET_{id}_response.json"
        )
        stack = self.client.v3.stacks.get("stack-id")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual("my-stack", stack["name"])
        self.assertIsInstance(stack, Entity)

    def test_update(self):
        self.client.patch.return_value = self.mock_response(
            "/v3/stacks/stack-id", HTTPStatus.OK, None,
            "v3", "stacks", "PATCH_{id}_response.json"
        )
        result = self.client.v3.stacks.update("stack-id",
                                              {"key": "value"},
                                              {"note": "detailed information"}
                                              )
        self.client.patch.assert_called_with(
            self.client.patch.return_value.url,
            json={
                "metadata": {
                    "labels": {"key": "value"},
                    "annotations": {"note": "detailed information"}
                }
            }
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)

    def test_list_apps(self):
        self.client.get.return_value = self.mock_response(
            "/v3/stacks/stack-id/apps", HTTPStatus.OK, None,
            "v3", "stacks", "GET_{id}_apps_response.json"
        )
        all_apps = [app for app in self.client.v3.stacks.list_apps('stack-id')]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_apps))
        self.assertEqual(all_apps[0]["name"], "my_app")
        self.assertIsInstance(all_apps[0], Entity)

    def test_remove(self):
        self.client.delete.return_value = self.mock_response("/v3/stacks/stack-id",
                                                             HTTPStatus.NO_CONTENT, None)
        self.client.v3.stacks.remove("stack-id")
        self.client.delete.assert_called_with(self.client.delete.return_value.url)
