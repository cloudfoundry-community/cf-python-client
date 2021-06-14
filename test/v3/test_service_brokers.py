import unittest
from http import HTTPStatus

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.entities import Entity


class TestServiceBrokers(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_create(self):
        self.client.post.return_value = self.mock_response(
            "/v3/service_brokers", HTTPStatus.OK, None, "v3", "service_brokers", "POST_response.json"
        )
        username = "us3rn4me"
        password = "p4ssw0rd"
        url = "https://example.service-broker.com"
        result = self.client.v3.service_brokers.create("my_service_broker", url, username, password)
        self.client.post.assert_called_with(
            self.client.post.return_value.url,
            files=None,
            json={
                "name": "my_service_broker",
                "url": url,
                "authentication": {"type": "basic", "credentials": {"username": username, "password": password}},
            },
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)

    def test_create_with_space_guid(self):
        self.client.post.return_value = self.mock_response(
            "/v3/service_brokers", HTTPStatus.OK, None, "v3", "service_brokers", "POST_response.json"
        )
        username = "us3rn4me"
        password = "p4ssw0rd"
        url = "https://example.service-broker.com"
        result = self.client.v3.service_brokers.create("my_service_broker", url, username, password, "space-guid-123")
        relationships = {"space": {"data": {"guid": "space-guid-123"}}}
        self.client.post.assert_called_with(
            self.client.post.return_value.url,
            files=None,
            json={
                "name": "my_service_broker",
                "url": url,
                "authentication": {"type": "basic", "credentials": {"username": username, "password": password}},
                "relationships": relationships,
            },
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)

    def test_list(self):
        self.client.get.return_value = self.mock_response(
            "/v3/service_brokers", HTTPStatus.OK, None, "v3", "service_brokers", "GET_response.json"
        )
        all_service_brokers = [service_broker for service_broker in self.client.v3.service_brokers.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_service_brokers))
        self.assertEqual(all_service_brokers[0]["name"], "my_service_broker")
        self.assertIsInstance(all_service_brokers[0], Entity)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v3/service_brokers/service_broker_guid_123", HTTPStatus.OK, None, "v3", "service_brokers", "GET_{id}_response.json"
        )
        service_broker = self.client.v3.service_brokers.get("service_broker_guid_123")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual("my_service_broker", service_broker["name"])
        self.assertIsInstance(service_broker, Entity)

    def test_update_service_broker_metadata(self):
        self.client.patch.return_value = self.mock_response(
            "/v3/service_brokers/service_broker_guid_123",
            HTTPStatus.OK,
            None,
            "v3",
            "service_brokers",
            "PATCH_{id}_response.json",
        )
        service_broker = self.client.v3.service_brokers.update(guid="service_broker_guid_123", meta_labels={"hello": "world"})
        self.client.patch.assert_called_with(
            self.client.patch.return_value.url,
            json={"metadata": {"labels": {"hello": "world"}}},
        )
        self.assertIsNotNone(service_broker)
        self.assertIsInstance(service_broker, Entity)

    def test_update_service_broker_name(self):
        self.client.patch.return_value = self.mock_response(
            "/v3/service_brokers/service_broker_guid_123",
            HTTPStatus.OK,
            headers={"Location": "http://localhost/v3/jobs/job-guid-123"},
        )
        service_broker = self.client.v3.service_brokers.update(guid="service_broker_guid_123", name="my_service_broker")
        self.client.patch.assert_called_with(
            self.client.patch.return_value.url,
            json={"name": "my_service_broker"},
        )
        self.assertIsNotNone(service_broker)
        self.assertIsInstance(service_broker, Entity)

    def test_remove(self):
        self.client.delete.return_value = self.mock_response("/v3/service_brokers/service_broker_id", HTTPStatus.NO_CONTENT, None)
        self.client.v3.service_brokers.remove("service_broker_id")
        self.client.delete.assert_called_with(self.client.delete.return_value.url)
