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

    def test_create(self):
        self.client.post.return_value = self.mock_response(
            "/v3/service_instances",
            HTTPStatus.ACCEPTED,
            headers={"Location": "https://somewhere.org/v3/jobs/job_id"},
        )
        result = self.client.v3.service_instances.create(
            name="space-name",
            parameters={"foo": "bar"},
            tags=["mytag", "myothertag"],
            space_guid="space-guid-123",
            service_plan_guid="service-plan-guid-123",
        )
        self.client.post.assert_called_with(
            self.client.post.return_value.url,
            json={
                "name": "space-name",
                "parameters": {"foo": "bar"},
                "tags": ["mytag", "myothertag"],
                "type": "managed",
                "relationships": {
                    "space": {"data": {"guid": "space-guid-123"}},
                    "service_plan": {"data": {"guid": "service-plan-guid-123"}},
                },
            },
            files=None,
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)

    def test_update(self):
        self.client.patch.return_value = self.mock_response(
            "/v3/service_instances/instance-guid-123",
            HTTPStatus.ACCEPTED,
            headers={"Location": "https://somewhere.org/v3/jobs/job_id"},
        )
        result = self.client.v3.service_instances.update(
            instance_guid="instance-guid-123",
            name="space-name",
            parameters={"foo": "bar"},
            service_plan="custom_service_plan",
            maintenance_info="1.2.3",
            meta_labels={"foo": "bar"},
            meta_annotations={"foo": "bar"},
            tags=["mytag", "myothertag"],
        )

        self.client.patch.assert_called_with(
            self.client.patch.return_value.url,
            json={
                "name": "space-name",
                "parameters": {"foo": "bar"},
                "relationships": {
                    "service_plan": {
                        "data": {"guid": "custom_service_plan"}},
                },
                "maintenance_info": {"version": "1.2.3"},
                "tags": ["mytag", "myothertag"],
                "metadata": {'labels': {'foo': 'bar'},
                             'annotations': {'foo': 'bar'}}
            },
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)

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
