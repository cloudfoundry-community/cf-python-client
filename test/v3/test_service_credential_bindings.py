import unittest
from http import HTTPStatus

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.service_credential_bindings import ServiceCredentialBinding


class TestCredentialBindings(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = self.mock_response(
            "/v3/service_credential_bindings", HTTPStatus.OK, None, "v3", "service_credential_bindings",
            "GET_response.json"
        )
        all_service_credential_bindings = [credential_binding for credential_binding in
                                           self.client.v3.service_credential_bindings.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_service_credential_bindings))
        self.assertEqual(all_service_credential_bindings[0]["name"], "some-binding-name")
        for domain in all_service_credential_bindings:
            self.assertIsInstance(domain, ServiceCredentialBinding)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v3/service_credential_bindings/service_credential_binding_id",
            HTTPStatus.OK,
            None,
            "v3",
            "service_credential_bindings", "GET_{id}_response.json"
        )
        result = self.client.v3.service_credential_bindings.get("service_credential_binding_id")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ServiceCredentialBinding)

    def test_get_then_details(self):
        get_service_credential_binding = self.mock_response(
            "/v3/service_credential_bindings/service_credential_binding_id",
            HTTPStatus.OK,
            None,
            "v3",
            "service_credential_bindings",
            "GET_{id}_response.json")
        get_details = self.mock_response(
            "/v3/service_credential_bindings/service_credential_binding_id/details",
            HTTPStatus.OK,
            None,
            "v3",
            "service_credential_bindings",
            "GET_{id}_details_response.json",
        )
        self.client.get.side_effect = [get_service_credential_binding, get_details]
        service_credential_binding = self.client.v3.service_credential_bindings.get("service_credential_binding_id")
        details = service_credential_binding.details()
        self.assertIsInstance(details, dict)
        self.assertEqual("mydb://user@password:example.com", details["credentials"]["connection"])

    def test_get_then_parameters(self):
        get_service_credential_binding = self.mock_response(
            "/v3/service_credential_bindings/service_credential_binding_id",
            HTTPStatus.OK,
            None, "v3",
            "service_credential_bindings",
            "GET_{id}_response.json")
        get_parameters = self.mock_response(
            "/v3/service_credential_bindings/service_credential_binding_id/parameters",
            HTTPStatus.OK,
            None,
            "v3",
            "service_credential_bindings",
            "GET_{id}_parameters_response.json",
        )
        self.client.get.side_effect = [get_service_credential_binding, get_parameters]
        service_credential_binding = self.client.v3.service_credential_bindings.get("service_credential_binding_id")
        parameters = service_credential_binding.parameters()
        self.assertIsInstance(parameters, dict)
        self.assertEqual("bar", parameters["foo"])
