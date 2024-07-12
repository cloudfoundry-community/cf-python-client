import unittest
from http import HTTPStatus

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.entities import Entity


class TestServiceOfferings(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v3/service_offerings/service_offering_guid",
            HTTPStatus.OK,
            None,
            "v3",
            "service_offerings",
            "GET_{id}_response.json",
        )
        service_offering = self.client.v3.service_offerings.get("service_offering_guid")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual("my_service_offering", service_offering["name"])
        self.assertIsInstance(service_offering, Entity)

    def test_list(self):
        self.client.get.return_value = self.mock_response(
            "/v3/service_offerings", HTTPStatus.OK, None, "v3", "service_offerings", "GET_response.json"
        )
        all_service_offerings = [service_offerings for service_offerings in self.client.v3.service_offerings.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_service_offerings))
        self.assertEqual(all_service_offerings[0]["name"], "my_service_offering")
        self.assertIsInstance(all_service_offerings[0], Entity)

    def test_update(self):
        self.client.patch.return_value = self.mock_response(
            "/v3/service_offerings/service_offering_guid",
            HTTPStatus.OK,
            None,
            "v3",
            "service_offerings",
            "PATCH_{id}_response.json",
        )
        service_offering = self.client.v3.service_offerings.update(guid="service_offering_guid", meta_labels={"hello": "world"})
        self.client.patch.assert_called_with(
            self.client.patch.return_value.url,
            json={"metadata": {"labels": {"hello": "world"}}},
        )
        self.assertIsNotNone(service_offering)
        self.assertIsInstance(service_offering, Entity)

    def test_remove(self):
        self.client.delete.return_value = self.mock_response(
            "/v3/service_offerings/service_offering_guid", HTTPStatus.NO_CONTENT, None
        )
        self.client.v3.service_offerings.remove(guid="service_offering_guid", purge=True)
        self.client.delete.assert_called_with(
            f"{self.client.delete.return_value.url}?purge=true",
        )
