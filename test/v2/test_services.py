import sys
import unittest
from functools import reduce
from http import HTTPStatus
from unittest.mock import call, patch

import cloudfoundry_client.main.main as main
from abstract_test_case import AbstractTestCase


class TestServices(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = self.mock_response(
            "/v2/services?q=label%3Asome_label", HTTPStatus.OK, None, "v2", "services", "GET_response.json"
        )
        cpt = reduce(lambda increment, _: increment + 1, self.client.v2.services.list(label="some_label"), 0)
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v2/services/service_id", HTTPStatus.OK, None, "v2", "services", "GET_{id}_response.json"
        )
        result = self.client.v2.services.get("service_id")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)

    def test_entity(self):
        self.client.get.side_effect = [
            self.mock_response("/v2/services/service_id", HTTPStatus.OK, None, "v2", "services", "GET_{id}_response.json"),
            self.mock_response(
                "/v2/services/2c883dbb-a726-4ecf-a0b7-d65588897e7f/service_plans",
                HTTPStatus.OK,
                None,
                "v2",
                "service_plans",
                "GET_response.json",
            ),
        ]
        service = self.client.v2.services.get("service_id")
        cpt = reduce(lambda increment, _: increment + 1, service.service_plans(), 0)
        self.assertEqual(cpt, 1)
        self.client.get.assert_has_calls([call(side_effect.url) for side_effect in self.client.get.side_effect], any_order=False)

    @patch.object(sys, "argv", ["main", "list_services"])
    def test_main_list_services(self):
        with patch("cloudfoundry_client.main.main.build_client_from_configuration", new=lambda: self.client):
            self.client.get.return_value = self.mock_response(
                "/v2/services", HTTPStatus.OK, None, "v2", "services", "GET_response.json"
            )
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)

    @patch.object(sys, "argv", ["main", "get_service", "2c883dbb-a726-4ecf-a0b7-d65588897e7f"])
    def test_main_get_service(self):
        with patch("cloudfoundry_client.main.main.build_client_from_configuration", new=lambda: self.client):
            self.client.get.return_value = self.mock_response(
                "/v2/services/2c883dbb-a726-4ecf-a0b7-d65588897e7f",
                HTTPStatus.OK,
                None,
                "v2",
                "services",
                "GET_{id}_response.json",
            )
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)
