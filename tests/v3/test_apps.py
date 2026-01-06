import unittest
import yaml
from http import HTTPStatus
from typing import List

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.common_objects import JsonObject, Pagination
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

    def test_get_then_environment_variables(self):
        get_app = self.mock_response("/v3/apps/app_id", HTTPStatus.OK, None, "v3", "apps", "GET_{id}_response.json")
        get_environment_variables = self.mock_response(
            "/v3/apps/app_id/environment_variables",
            HTTPStatus.OK,
            None,
            "v3",
            "apps",
            "GET_{id}_environment_variables_response.json",
        )
        self.client.get.side_effect = [get_app, get_environment_variables]
        app = self.client.v3.apps.get("app_id")
        environment_variables = app.environment_variables()
        self.assertIsInstance(environment_variables, dict)
        self.assertEqual("production", environment_variables["var"]["RAILS_ENV"])

    def test_restart(self):
        self.client.post.return_value = self.mock_response(
            "/v3/apps/app_id/actions/restart", HTTPStatus.OK, None, "v3", "apps",
            "GET_{id}_response.json"
        )

        app = self.client.v3.apps.restart("app_id")
        self.assertIsInstance(app, JsonObject)
        self.assertEqual("my_app", app["name"])

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
        self.assertEqual(env["application_env_json"]["VCAP_APPLICATION"]["limits"]["fds"], 16384)

    def test_get_routes(self):
        self.client.get.return_value = self.mock_response(
            "/v3/apps/app_id/routes", HTTPStatus.OK, None, "v3", "apps", "GET_{id}_routes_response.json"
        )
        routes = self.client.v3.apps.get_routes("app_id")
        self.assertIsInstance(routes, JsonObject)
        self.assertEqual(routes["resources"][0]["destinations"][0]["guid"], "385bf117-17f5-4689-8c5c-08c6cc821fed")

    def test_get_include_space_and_org(self):
        self.client.get.return_value = self.mock_response(
            "/v3/apps/app_id?include=space.organization",
            HTTPStatus.OK,
            None,
            "v3",
            "apps",
            "GET_{id}_response_include_space_and_org.json"
        )
        space = self.client.v3.apps.get("app_id", include="space.organization").space()
        self.client.get.assert_called_with(self.client.get.return_value.url)
        org = space.organization()
        self.assertEqual("my_space", space["name"])
        self.assertIsInstance(space, Entity)
        self.assertEqual("my_organization", org["name"])
        self.assertIsInstance(org, Entity)

    def test_list_include_space(self):
        self.client.get.return_value = self.mock_response(
            "/v3/apps?include=space", HTTPStatus.OK, None, "v3", "apps", "GET_response_include_space.json"
        )
        all_spaces = [app.space() for app in self.client.v3.apps.list(include="space")]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_spaces))
        self.assertEqual(all_spaces[0]["name"], "my_space")
        self.assertIsInstance(all_spaces[0], Entity)
        self.assertEqual(all_spaces[1]["name"], "my_space")
        self.assertIsInstance(all_spaces[1], Entity)

    def test_get_manifest(self):
        self.client.get.return_value = self.mock_response(
            "/v3/apps/app_id/manifest", HTTPStatus.OK, {"Content-Type": "application/x-yaml"}, "v3", "apps",
            "GET_{id}_manifest_response.yml"
        )
        manifest_response: str = self.client.v3.apps.get_manifest("app_id")
        self.assertIsInstance(manifest_response, str)
        manifest: dict = yaml.safe_load(manifest_response)
        applications: list[dict] | None = manifest.get("applications")
        self.assertIsInstance(applications, list)
        self.assertEqual(len(applications), 1)
        application: dict = applications[0]
        self.assertEqual(application.get("name"), "my-app")
        self.assertEqual(application.get("stack"), "cflinuxfs4")
        application_services: list[str] | None = application.get("services")
        self.assertIsInstance(application_services, list)
        self.assertEqual(len(application_services), 1)
        self.assertEqual(application_services[0], "my-service")
        application_routes: List[dict | str] | None = application.get("routes")
        self.assertIsInstance(application_routes, list)
        self.assertEqual(len(application_routes), 1)
        application_route: dict = application_routes[0]
        self.assertIsInstance(application_route, dict)
        self.assertEqual(application_route.get("route"), "my-app.example.com")
        self.assertEqual(application_route.get("protocol"), "http1")

    def test_list_revisions(self):
        self.client.get.return_value = self.mock_response(
            "/v3/apps/app_guid/revisions", HTTPStatus.OK, {"Content-Type": "application/json"}, "v3", "apps",
            "GET_{id}_revisions_response.json"
        )
        revisions_response: Pagination[Entity] = self.client.v3.apps.list_revisions("app_guid")
        revisions: list[dict] = [revision for revision in revisions_response]
        self.assertIsInstance(revisions, list)
        self.assertEqual(len(revisions), 1)
        revision: dict = revisions[0]
        self.assertIsInstance(revision, dict)
        self.assertEqual(revision.get("guid"), "885735b5-aea4-4cf5-8e44-961af0e41920")
        self.assertEqual(revision.get("description"), "Initial revision.")
        self.assertEqual(revision.get("deployable"), True)

    def test_list_deployed_revisions(self):
        self.client.get.return_value = self.mock_response(
            "/v3/apps/app_guid/revisions/deployed", HTTPStatus.OK, {"Content-Type": "application/json"}, "v3", "apps",
            "GET_{id}_deployed_revisions_response.json"
        )
        revisions_response: Pagination[Entity] = self.client.v3.apps.list_deployed_revisions("app_guid")
        revisions: list[dict] = [revision for revision in revisions_response]
        self.assertIsInstance(revisions, list)
        self.assertEqual(len(revisions), 1)
        revision: dict = revisions[0]
        self.assertIsInstance(revision, dict)
        self.assertEqual(revision.get("created_at"), "2017-02-01T01:33:58Z")
        self.assertEqual(revision.get("version"), 1)
