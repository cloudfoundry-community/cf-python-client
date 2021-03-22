import unittest
from http import HTTPStatus
from unittest.mock import patch
from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.entities import Entity


class TestServiceInstances(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = self.mock_response(
            "/v3/service_instances", HTTPStatus.OK, None, "v3", "service_instances", "GET_response.json"
        )
        all_service_instances = [service_instance for service_instance in self.client.v3.service_instances.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(1, len(all_service_instances))
        self.assertEqual(all_service_instances[0]["guid"], "85ccdcad-d725-4109-bca4-fd6ba062b5c8")
        self.assertIsInstance(all_service_instances[0], Entity)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v3/service_instances/service_instance_id", HTTPStatus.OK, None, "v3", "service_instances", "GET_{id}_response.json"
        )
        service_instance = self.client.v3.service_instances.get("service_instance_id")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual("85ccdcad-d725-4109-bca4-fd6ba062b5c8", service_instance["guid"])
        self.assertIsInstance(service_instance, Entity)

    def test_remove_user_provided_service_instance(self):
        self.client.delete.return_value = self.mock_response(
            "/v3/service_instances/service_instance_id", HTTPStatus.NO_CONTENT, None
        )
        self.client.v3.service_instances.remove("service_instance_id")
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    def test_remove(self):
        self.client.delete.return_value = self.mock_response(
            "/v3/service_instances/service_instance_id",
            HTTPStatus.ACCEPTED,
            headers={"Location": "https://somewhere.org/v3/jobs/job_id"},
        )
        self.client.v3.service_instances.remove("service_instance_id")
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    @patch("time.sleep", return_value=None)
    def test_remove_synchronous(self, sleepmock):
        self.client.delete.return_value = self.mock_response(
            "/v3/service_instances/service_instance_id", HTTPStatus.ACCEPTED, {"Location": "https://somewhere.org/v3/jobs/job_id"}
        )
        self.client.get.side_effect = [
            self.mock_response(
                "/v3/jobs/job_id",
                HTTPStatus.OK,
                None,
                "v3",
                "jobs",
                "GET_{id}_processing_response.json",
            ),
            self.mock_response(
                "/v3/jobs/job_id",
                HTTPStatus.OK,
                None,
                "v3",
                "jobs",
                "GET_{id}_complete_response.json",
            ),
        ]
        self.client.v3.service_instances.remove("service_instance_id", asynchronous=False)
        self.client.delete.assert_called_with(self.client.delete.return_value.url)
        assert self.client.get.call_count == 2
