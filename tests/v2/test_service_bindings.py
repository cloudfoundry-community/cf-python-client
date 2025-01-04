import sys
import unittest
from functools import reduce
from http import HTTPStatus
from unittest.mock import call, patch

import cloudfoundry_client.main.main as main
from abstract_test_case import AbstractTestCase


class TestServiceBindings(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = self.mock_response(
            "/v2/service_bindings?q=service_instance_guid%3Ainstance_guid",
            HTTPStatus.OK,
            None,
            "v2",
            "service_bindings",
            "GET_response.json",
        )
        cpt = reduce(
            lambda increment, _: increment + 1, self.client.v2.service_bindings.list(service_instance_guid="instance_guid"), 0
        )
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v2/service_bindings/service_binding_id", HTTPStatus.OK, None, "v2", "service_bindings", "GET_{id}_response.json"
        )
        result = self.client.v2.service_bindings.get("service_binding_id")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)

    def test_create(self):
        self.client.post.return_value = self.mock_response(
            "/v2/service_bindings", HTTPStatus.CREATED, None, "v2", "service_bindings", "POST_response.json"
        )
        service_binding = self.client.v2.service_bindings.create(
            "app_guid", "instance_guid", dict(the_service_broker="wants this object"), "binding_name"
        )
        self.client.post.assert_called_with(
            self.client.post.return_value.url,
            json=dict(
                app_guid="app_guid",
                service_instance_guid="instance_guid",
                name="binding_name",
                parameters=dict(the_service_broker="wants this object"),
            ),
        )
        self.assertIsNotNone(service_binding)

    def test_delete(self):
        self.client.delete.return_value = self.mock_response("/v2/service_bindings/binding_id", HTTPStatus.NO_CONTENT, None)
        self.client.v2.service_bindings.remove("binding_id")
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    def test_entity(self):
        self.client.get.side_effect = [
            self.mock_response(
                "/v2/service_bindings/service_binding_id", HTTPStatus.OK, None, "v2", "service_bindings", "GET_{id}_response.json"
            ),
            self.mock_response(
                "/v2/service_instances/ef0bf611-82c6-4603-99fc-3a1a893109d0",
                HTTPStatus.OK,
                None,
                "v2",
                "service_instances",
                "GET_{id}_response.json",
            ),
            self.mock_response(
                "/v2/apps/c77953c8-6c35-46c7-816e-cf0c42ac2f52", HTTPStatus.OK, None, "v2", "apps", "GET_{id}_response.json"
            ),
        ]
        service_binding = self.client.v2.service_bindings.get("service_binding_id")
        self.assertIsNotNone(service_binding.service_instance())
        self.assertIsNotNone(service_binding.app())
        self.client.get.assert_has_calls([call(side_effect.url) for side_effect in self.client.get.side_effect], any_order=False)

    @patch.object(sys, "argv", ["main", "list_service_bindings"])
    def test_main_list_service_bindings(self):
        with patch("cloudfoundry_client.main.main.build_client_from_configuration", new=lambda: self.client):
            self.client.get.return_value = self.mock_response(
                "/v2/service_bindings", HTTPStatus.OK, None, "v2", "service_bindings", "GET_response.json"
            )
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)

    @patch.object(sys, "argv", ["main", "get_service_binding", "eaabd042-8f5c-44a2-9580-1e114c36bdcb"])
    def test_main_get_service_binding(self):
        with patch("cloudfoundry_client.main.main.build_client_from_configuration", new=lambda: self.client):
            self.client.get.return_value = self.mock_response(
                "/v2/service_bindings/eaabd042-8f5c-44a2-9580-1e114c36bdcb",
                HTTPStatus.OK,
                None,
                "v2",
                "service_bindings",
                "GET_{id}_response.json",
            )
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)
