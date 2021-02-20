import unittest
from http import HTTPStatus

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.json_object import JsonObject
from cloudfoundry_client.v3.entities import Entity


class TestApps(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = self.mock_response("/v3/apps", HTTPStatus.OK, None, "v3", "apps", "GET_response.json")
        all_applications = [application for application in self.client.v3.apps.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_applications))
        self.assertEqual(all_applications[0]["name"], "my_app")
        self.assertIsInstance(all_applications[0], Entity)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v3/apps/app_id", HTTPStatus.OK, None, "v3", "apps", "GET_{id}_response.json"
        )
        application = self.client.v3.apps.get("app_id")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual("my_app", application["name"])
        self.assertIsInstance(application, Entity)

    def test_get_then_space(self):
        get_app = self.mock_response("/v3/apps/app_id", HTTPStatus.OK, None, "v3", "apps", "GET_{id}_response.json")
        get_space = self.mock_response(
            "/v3/spaces/2f35885d-0c9d-4423-83ad-fd05066f8576", HTTPStatus.OK, None, "v3", "spaces", "GET_{id}_response.json"
        )
        self.client.get.side_effect = [get_app, get_space]
        space = self.client.v3.apps.get("app_id").space()
        # self.client.get.assert_has_calls([call(get_app.url),
        #                                   call(get_space.url)],
        #                                  any_order=False)
        self.assertEqual("my-space", space["name"])

    def test_get_then_start(self):
        self.client.get.return_value = self.mock_response(
            "/v3/apps/app_id", HTTPStatus.OK, None, "v3", "apps", "GET_{id}_response.json"
        )
        self.client.post.return_value = self.mock_response(
            "/v3/apps/app_id/actions/start", HTTPStatus.OK, None, "v3", "apps", "POST_{id}_actions_start_response.json"
        )

        app = self.client.v3.apps.get("app_id").start()
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.client.post.assert_called_with(self.client.post.return_value.url, files=None, json=None)
        self.assertEqual("my_app", app["name"])
        self.assertIsInstance(app, Entity)

    def test_remove(self):
        self.client.delete.return_value = self.mock_response("/v3/apps/app_id", HTTPStatus.NO_CONTENT, None)
        self.client.v3.apps.remove("app_id")
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    def test_get_env(self):
        self.client.get.return_value = self.mock_response(
            "/v3/apps/app_id/env", HTTPStatus.OK, None, "v3", "apps", "GET_{id}_env_response.json"
        )
        env = self.client.v3.apps.get_env("app_id")
        self.assertIsInstance(env, JsonObject)
        self.assertEquals(env["application_env_json"]["VCAP_APPLICATION"]["limits"]["fds"], 16384)

    def test_get_routes(self):
        self.client.get.return_value = self.mock_response(
            "/v3/apps/app_id/routes", HTTPStatus.OK, None, "v3", "apps", "GET_{id}_routes_response.json"
        )
        routes = self.client.v3.apps.get_routes("app_id")
        self.assertIsInstance(routes, JsonObject)
        self.assertEquals(routes["resources"][0]["destinations"][0]["guid"], "385bf117-17f5-4689-8c5c-08c6cc821fed")
