import json
import sys
import unittest
from functools import reduce
from http import HTTPStatus
from unittest.mock import patch

import cloudfoundry_client.main.main as main
from abstract_test_case import AbstractTestCase


class TestServiceKeys(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = self.mock_response(
            "/v2/service_keys?q=service_instance_guid%3Ainstance_guid",
            HTTPStatus.OK,
            None,
            "v2",
            "service_keys",
            "GET_response.json",
        )
        cpt = reduce(
            lambda increment, _: increment + 1, self.client.v2.service_keys.list(service_instance_guid="instance_guid"), 0
        )
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v2/service_keys/key_id", HTTPStatus.OK, None, "v2", "service_keys", "GET_{id}_response.json"
        )
        result = self.client.v2.service_keys.get("key_id")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)

    def test_create(self):
        self.client.post.return_value = self.mock_response(
            "/v2/service_keys", HTTPStatus.CREATED, None, "v2", "service_keys", "POST_response.json"
        )
        service_key = self.client.v2.service_keys.create("service_instance_id", "name-127")
        self.client.post.assert_called_with(
            self.client.post.return_value.url, json=dict(service_instance_guid="service_instance_id", name="name-127")
        )
        self.assertIsNotNone(service_key)

    def test_delete(self):
        self.client.delete.return_value = self.mock_response("/v2/service_keys/key_id", HTTPStatus.NO_CONTENT, None)
        self.client.v2.service_keys.remove("key_id")
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    @patch.object(sys, "argv", ["main", "list_service_keys"])
    def test_main_list_service_keys(self):
        with patch("cloudfoundry_client.main.main.build_client_from_configuration", new=lambda: self.client):
            self.client.get.return_value = self.mock_response(
                "/v2/service_keys", HTTPStatus.OK, None, "v2", "service_keys", "GET_response.json"
            )
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)

    @patch.object(sys, "argv", ["main", "get_service_key", "67755c27-28ed-4087-9688-c07d92f3bcc9"])
    def test_main_get_service_key(self):
        with patch("cloudfoundry_client.main.main.build_client_from_configuration", new=lambda: self.client):
            self.client.get.return_value = self.mock_response(
                "/v2/service_keys/67755c27-28ed-4087-9688-c07d92f3bcc9",
                HTTPStatus.OK,
                None,
                "v2",
                "service_keys",
                "GET_{id}_response.json",
            )
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)

    @patch.object(
        sys,
        "argv",
        ["main", "create_service_key", json.dumps(dict(service_instance_guid="service_instance_id", name="name-127"))],
    )
    def test_main_create_service_key(self):
        with patch("cloudfoundry_client.main.main.build_client_from_configuration", new=lambda: self.client):
            self.client.post.return_value = self.mock_response(
                "/v2/service_keys", HTTPStatus.CREATED, None, "v2", "service_keys", "POST_response.json"
            )
            main.main()
            self.client.post.assert_called_with(
                self.client.post.return_value.url, json=dict(service_instance_guid="service_instance_id", name="name-127")
            )

    @patch.object(sys, "argv", ["main", "delete_service_key", "67755c27-28ed-4087-9688-c07d92f3bcc9"])
    def test_main_delete_service_key(self):
        with patch("cloudfoundry_client.main.main.build_client_from_configuration", new=lambda: self.client):
            self.client.delete.return_value = self.mock_response(
                "/v2/service_keys/67755c27-28ed-4087-9688-c07d92f3bcc9", HTTPStatus.NO_CONTENT, None
            )
            main.main()
            self.client.delete.assert_called_with(self.client.delete.return_value.url)
            main.main()
