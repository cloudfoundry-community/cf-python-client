import unittest
from http import HTTPStatus

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.entities import Entity


class TestServicePlans(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v3/service_plans/service_plan_guid_123", HTTPStatus.OK, None, "v3", "service_plans", "GET_{id}_response.json"
        )
        service_plan = self.client.v3.service_plans.get("service_plan_guid_123")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual("my_service_plan", service_plan["name"])
        self.assertIsInstance(service_plan, Entity)

    def test_list(self):
        self.client.get.return_value = self.mock_response(
            "/v3/service_plans", HTTPStatus.OK, None, "v3", "service_plans", "GET_response.json"
        )
        all_service_plans = [service_plan for service_plan in self.client.v3.service_plans.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_service_plans))
        self.assertEqual(all_service_plans[0]["name"], "my_big_service_plan")
        self.assertIsInstance(all_service_plans[0], Entity)

    def test_update_service_plan(self):
        self.client.patch.return_value = self.mock_response(
            "/v3/service_plans/service_plan_guid_123", HTTPStatus.OK, None, "v3", "service_plans", "PATCH_{id}_response.json"
        )
        service_plan = self.client.v3.service_plans.update(
            guid="service_plan_guid_123", meta_labels={"hello": "world"}, meta_annotations={"note": "detailed information"}
        )
        self.client.patch.assert_called_with(
            self.client.patch.return_value.url,
            json={"metadata": {"labels": {"hello": "world"}, "annotations": {"note": "detailed information"}}},
        )
        self.assertIsNotNone(service_plan)
        self.assertIsInstance(service_plan, Entity)

    def test_remove(self):
        self.client.delete.return_value = self.mock_response("/v3/service_plans/service_plan_id", HTTPStatus.NO_CONTENT, None)
        self.client.v3.service_plans.remove("service_plan_id")
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    def test_get_service_plan_visibility(self):
        self.client.get.return_value = self.mock_response(
            "/v3/service_plans/service_plan_guid_123/visibility",
            HTTPStatus.NO_CONTENT,
            None,
            "v3",
            "service_plans",
            "GET_{id}_visibility_response.json",
        )
        service_plan_visibility = self.client.v3.service_plans.get_visibility(service_plan_guid="service_plan_guid_123")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual("public", service_plan_visibility["type"])

    def test_update_service_plan_visibility_type(self):
        self.client.patch.return_value = self.mock_response(
            "/v3/service_plans/service_plan_guid_123/visibility",
            HTTPStatus.NO_CONTENT,
            None,
            "v3",
            "service_plans",
            "PATCH_{id}_visibility_type_response.json",
        )
        service_plan_visibility = self.client.v3.service_plans.update_visibility(
            service_plan_guid="service_plan_guid_123", type="admin"
        )
        self.client.patch.assert_called_with(self.client.patch.return_value.url, json={"type": "admin"})
        self.assertEqual("admin", service_plan_visibility["type"])

    def test_update_service_plan_visibility_organizations(self):
        self.client.patch.return_value = self.mock_response(
            "/v3/service_plans/service_plan_guid_123/visibility",
            HTTPStatus.NO_CONTENT,
            None,
            "v3",
            "service_plans",
            "PATCH_{id}_visibility_organizations_response.json",
        )
        organizations = [{"guid": "0fc1ad4f-e1d7-4436-8e23-6b20f03c6482"}, {"guid": "0fc1ad4f-e1d7-4436-8e23-6b20f03c6483"}]
        service_plan_visibility = self.client.v3.service_plans.update_visibility(
            service_plan_guid="service_plan_guid_123", type="organization", organizations=organizations
        )
        self.client.patch.assert_called_with(
            self.client.patch.return_value.url, json={"type": "organization", "organizations": organizations}
        )
        self.assertEqual("organization", service_plan_visibility["type"])
        self.assertEqual("some_org", service_plan_visibility["organizations"][0]["name"])

    def test_apply_visibility_to_extra_orgs(self):
        self.client.post.return_value = self.mock_response(
            "/v3/service_plans/service_plan_guid_123/visibility",
            HTTPStatus.NO_CONTENT,
            None,
            "v3",
            "service_plans",
            "POST_{id}_visibility_response.json",
        )
        organizations = [{"guid": "b3af3658-d844-496a-8986-89b79a74c8ae"}]
        service_plan_visibility = self.client.v3.service_plans.apply_visibility_to_extra_orgs(
            service_plan_guid="service_plan_guid_123", organizations=organizations
        )
        self.client.post.assert_called_with(
            self.client.post.return_value.url, json={"type": "organization", "organizations": organizations}, files=None
        )
        self.assertEqual("organization", service_plan_visibility["type"])
        self.assertEqual("b3af3658-d844-496a-8986-89b79a74c8ae", service_plan_visibility["organizations"][0]["guid"])

    def test_remove_org_from_service_plan_visibility(self):
        self.client.delete.return_value = self.mock_response(
            "/v3/service_plans/service_plan_guid_123/visibility/org_guid_123", HTTPStatus.NO_CONTENT, None
        )
        self.client.v3.service_plans.remove_org_from_service_plan_visibility(
            service_plan_guid="service_plan_guid_123", org_guid="org_guid_123"
        )
        self.client.delete.assert_called_with(self.client.delete.return_value.url)
