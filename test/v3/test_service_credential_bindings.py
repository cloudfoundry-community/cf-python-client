import unittest
from http import HTTPStatus

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.entities import Entity


class TestCredentialBindings(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_create_managed_service_instance(self):
        self.client.post.return_value = self.mock_response(
            "/v3/service_credential_bindings", HTTPStatus.ACCEPTED,
            dict(Location="https://api.example.org/v3/jobs/af5c57f6-8769-41fa-a499-2c84ed896788")
        )
        location = self.client.v3.service_credential_bindings.create("some-binding-name", "app",
                                                                     "7304bc3c-7010-11ea-8840-48bf6bec2d78",
                                                                     "e0e4417c-74ee-11ea-a604-48bf6bec2d78",
                                                                     parameters=dict(key1="value1", key2="value2"),
                                                                     meta_labels=dict(foo="bar"),
                                                                     meta_annotations=dict(baz="qux"))

        self.assertEqual("af5c57f6-8769-41fa-a499-2c84ed896788", location)
        self.client.post.assert_called_with(
            self.client.post.return_value.url,
            json={
                "type": "app",
                "name": "some-binding-name",
                "relationships": {
                    "service_instance": {
                        "data": {"guid": "7304bc3c-7010-11ea-8840-48bf6bec2d78"}
                    },
                    "app": {
                        "data": {"guid": "e0e4417c-74ee-11ea-a604-48bf6bec2d78"}
                    }
                },
                "parameters": {"key1": "value1", "key2": "value2"},
                "metadata": {"labels": {"foo": "bar"}, "annotations": {"baz": "qux"}},
            },
        )

    def test_create_user_provided_service_instance(self):
        self.client.post.return_value = self.mock_response(
            "/v3/service_credential_bindings", HTTPStatus.ACCEPTED,
            None,
            "v3", "service_credential_bindings", "POST_response.json"
        )
        result = self.client.v3.service_credential_bindings.create("some-binding-name", "key",
                                                                   "7304bc3c-7010-11ea-8840-48bf6bec2d78",
                                                                   None,
                                                                   parameters=dict(key1="value1", key2="value2"),
                                                                   meta_labels=dict(foo="bar"),
                                                                   meta_annotations=dict(baz="qux"))
        self.assertIsNotNone(result)
        self.assertEqual("some-name", result["name"])
        self.assertIsInstance(result, Entity)
        self.client.post.assert_called_with(
            self.client.post.return_value.url,
            json={
                "type": "key",
                "name": "some-binding-name",
                "relationships": {
                    "service_instance": {
                        "data": {"guid": "7304bc3c-7010-11ea-8840-48bf6bec2d78"}
                    }
                },
                "parameters": {"key1": "value1", "key2": "value2"},
                "metadata": {"labels": {"foo": "bar"}, "annotations": {"baz": "qux"}},
            },
        )

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
            self.assertIsInstance(domain, Entity)

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
        self.assertIsInstance(result, Entity)

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
