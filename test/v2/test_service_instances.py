import sys
import unittest
from functools import reduce
from http import HTTPStatus
from unittest.mock import call, patch

import cloudfoundry_client.main.main as main
from abstract_test_case import AbstractTestCase


class TestServiceInstances(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = self.mock_response(
            "/v2/service_instances?q=service_plan_guid%3Aplan_id&q=space_guid%3Aspace_guid",
            HTTPStatus.OK,
            None,
            "v2",
            "service_instances",
            "GET_response.json",
        )
        cpt = reduce(
            lambda increment, _: increment + 1,
            self.client.v2.service_instances.list(space_guid="space_guid", service_plan_guid="plan_id"),
            0,
        )
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v2/service_instances/instance_id", HTTPStatus.OK, None, "v2", "service_instances", "GET_{id}_response.json"
        )
        result = self.client.v2.service_instances.get("instance_id")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)

    def test_create(self):
        self.client.post.return_value = self.mock_response(
            "/v2/service_instances", HTTPStatus.CREATED, None, "v2", "service_instances", "POST_response.json"
        )
        service_instance = self.client.v2.service_instances.create(
            "space_guid",
            "name",
            "plan_id",
            parameters=dict(the_service_broker="wants this object"),
            tags=["mongodb"],
            accepts_incomplete=True,
        )
        self.client.post.assert_called_with(
            self.client.post.return_value.url,
            json=dict(
                name="name",
                space_guid="space_guid",
                service_plan_guid="plan_id",
                parameters=dict(the_service_broker="wants this object"),
                tags=["mongodb"],
            ),
            params=dict(accepts_incomplete="true"),
        )
        self.assertIsNotNone(service_instance)

    def test_update(self):
        self.client.put.return_value = self.mock_response(
            "/v2/service_instances/instance_id", HTTPStatus.OK, None, "v2", "service_instances", "PUT_{id}_response.json"
        )
        service_instance = self.client.v2.service_instances.update("instance_id", instance_name="new-name", tags=["other-tag"])
        self.client.put.assert_called_with(
            self.client.put.return_value.url, json=dict(name="new-name", tags=["other-tag"]), params=None
        )
        self.assertIsNotNone(service_instance)

    def test_update2(self):
        self.client.put.return_value = self.mock_response(
            "/v2/service_instances/instance_id", HTTPStatus.OK, None, "v2", "service_instances", "PUT_{id}_response.json"
        )
        service_instance = self.client.v2.service_instances.update(
            "instance_id", instance_name="new-name", tags=["other-tag"], accepts_incomplete=True
        )
        self.client.put.assert_called_with(
            self.client.put.return_value.url,
            json=dict(name="new-name", tags=["other-tag"]),
            params={"accepts_incomplete": "true"},
        )
        self.assertIsNotNone(service_instance)

    def test_delete_accepts_incomplete(self):
        self.client.delete.return_value = self.mock_response("/v2/service_instances/instance_id", HTTPStatus.NO_CONTENT, None)
        self.client.v2.service_instances.remove("instance_id", accepts_incomplete=True)
        self.client.delete.assert_called_with(self.client.delete.return_value.url, params=dict(accepts_incomplete="true"))

        self.client.delete.return_value = self.mock_response("/v2/service_instances/instance_id", HTTPStatus.NO_CONTENT, None)
        self.client.v2.service_instances.remove("instance_id", accepts_incomplete="true")
        self.client.delete.assert_called_with(self.client.delete.return_value.url, params=dict(accepts_incomplete="true"))

    def test_delete_purge(self):
        self.client.delete.return_value = self.mock_response("/v2/service_instances/instance_id", HTTPStatus.NO_CONTENT, None)
        self.client.v2.service_instances.remove("instance_id", accepts_incomplete=True, purge=True)
        self.client.delete.assert_called_with(
            self.client.delete.return_value.url, params=dict(accepts_incomplete="true", purge="true")
        )

        self.client.delete.return_value = self.mock_response("/v2/service_instances/instance_id", HTTPStatus.NO_CONTENT, None)
        self.client.v2.service_instances.remove("instance_id", purge="true")
        self.client.delete.assert_called_with(self.client.delete.return_value.url, params=dict(purge="true"))

        self.client.delete.return_value = self.mock_response("/v2/service_instances/instance_id", HTTPStatus.NO_CONTENT, None)
        self.client.v2.service_instances.remove("instance_id", purge="true")
        self.client.delete.assert_called_with(self.client.delete.return_value.url, params=dict(purge="true"))

    def test_delete(self):
        self.client.delete.return_value = self.mock_response("/v2/service_instances/instance_id", HTTPStatus.NO_CONTENT, None)
        self.client.v2.service_instances.remove("instance_id")
        self.client.delete.assert_called_with(self.client.delete.return_value.url, params={})

    def test_entity(self):
        self.client.get.side_effect = [
            self.mock_response(
                "/v2/service_instances/instance_id", HTTPStatus.OK, None, "v2", "service_instances", "GET_{id}_response.json"
            ),
            self.mock_response(
                "/v2/spaces/e3138257-8035-4c03-8aba-ab5d35eec0f9", HTTPStatus.OK, None, "v2", "spaces", "GET_{id}_response.json"
            ),
            self.mock_response(
                "/v2/service_instances/df52420f-d5b9-4b86-a7d3-6d7005d1ce96/service_bindings",
                HTTPStatus.OK,
                None,
                "v2",
                "service_bindings",
                "GET_response.json",
            ),
            self.mock_response(
                "/v2/service_plans/65740f84-214a-46cf-b8e3-2233d580f293",
                HTTPStatus.OK,
                None,
                "v2",
                "service_plans",
                "GET_{id}_response.json",
            ),
            self.mock_response(
                "/v2/service_instances/df52420f-d5b9-4b86-a7d3-6d7005d1ce96/routes",
                HTTPStatus.OK,
                None,
                "v2",
                "routes",
                "GET_response.json",
            ),
            self.mock_response(
                "/v2/service_instances/df52420f-d5b9-4b86-a7d3-6d7005d1ce96/service_keys",
                HTTPStatus.OK,
                None,
                "v2",
                "service_keys",
                "GET_response.json",
            ),
        ]
        service_instance = self.client.v2.service_instances.get("instance_id")

        self.assertIsNotNone(service_instance.space())
        cpt = reduce(lambda increment, _: increment + 1, service_instance.service_bindings(), 0)
        self.assertEqual(cpt, 1)
        self.assertIsNotNone(service_instance.service_plan())
        cpt = reduce(lambda increment, _: increment + 1, service_instance.routes(), 0)
        self.assertEqual(cpt, 1)
        cpt = reduce(lambda increment, _: increment + 1, service_instance.service_keys(), 0)
        self.assertEqual(cpt, 1)
        self.client.get.assert_has_calls([call(side_effect.url) for side_effect in self.client.get.side_effect], any_order=False)

    @patch.object(sys, "argv", ["main", "list_service_instances"])
    def test_main_list_service_instances(self):
        with patch("cloudfoundry_client.main.main.build_client_from_configuration", new=lambda: self.client):
            self.client.get.return_value = self.mock_response(
                "/v2/service_instances", HTTPStatus.OK, None, "v2", "service_instances", "GET_response.json"
            )
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)

    @patch.object(sys, "argv", ["main", "get_service_instance", "df52420f-d5b9-4b86-a7d3-6d7005d1ce96"])
    def test_main_get_service_instance(self):
        with patch("cloudfoundry_client.main.main.build_client_from_configuration", new=lambda: self.client):
            self.client.get.return_value = self.mock_response(
                "/v2/service_instances/df52420f-d5b9-4b86-a7d3-6d7005d1ce96",
                HTTPStatus.OK,
                None,
                "v2",
                "service_instances",
                "GET_{id}_response.json",
            )
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)
