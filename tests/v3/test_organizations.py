import sys
import unittest
from http import HTTPStatus
from unittest.mock import patch

import cloudfoundry_client.main.main as main
from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.entities import Entity, ToOneRelationship


class TestOrganizations(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = self.mock_response(
            "/v3/organizations", HTTPStatus.OK, None, "v3", "organizations", "GET_response.json"
        )
        all_organizations = [organization for organization in self.client.v3.organizations.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_organizations))
        self.assertEqual(all_organizations[0]["name"], "org1")
        self.assertIsInstance(all_organizations[0], Entity)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v3/organizations/organization_id", HTTPStatus.OK, None, "v3", "organizations", "GET_{id}_response.json"
        )
        organization = self.client.v3.organizations.get("organization_id")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual("my-organization", organization["name"])
        self.assertIsInstance(organization, Entity)

    def test_update_without_optional_parameters(self):
        self.client.patch.return_value = self.mock_response(
            "/v3/organizations/organization_id", HTTPStatus.OK, None, "v3", "organizations", "PATCH_{id}_response.json"
        )
        result = self.client.v3.organizations.update("organization_id", "my-organization")
        self.client.patch.assert_called_with(
            self.client.patch.return_value.url,
            json={"name": "my-organization"},
        )
        self.assertIsNotNone(result)

    def test_update_with_optional_parameters(self):
        self.client.patch.return_value = self.mock_response(
            "/v3/organizations/organization_id", HTTPStatus.OK, None, "v3", "organizations", "PATCH_{id}_response.json"
        )
        result = self.client.v3.organizations.update(
            "organization_id",
            "my-organization",
            suspended=True,
            meta_labels={"label_name": "label_value"},
            meta_annotations={"annotation_name": "annotation_value"}
        )
        self.client.patch.assert_called_with(
            self.client.patch.return_value.url,
            json={
                "suspended": True,
                "name": "my-organization",
                "metadata": {
                    "labels": {"label_name": "label_value"},
                    "annotations": {"annotation_name": "annotation_value"}
                }
            },
        )
        self.assertIsNotNone(result)

    def test_create(self):
        self.client.post.return_value = self.mock_response(
            "/v3/organizations", HTTPStatus.OK, None, "v3", "organizations", "POST_response.json"
        )
        result = self.client.v3.organizations.create("my-organization", suspended=False)
        self.client.post.assert_called_with(
            self.client.post.return_value.url,
            files=None,
            json={"name": "my-organization", "suspended": False, "metadata": {"labels": None, "annotations": None}},
        )
        self.assertIsNotNone(result)

    def test_remove(self):
        self.client.delete.return_value = self.mock_response("/v3/organizations/organization_id", HTTPStatus.NO_CONTENT, None)
        self.client.v3.organizations.remove("organization_id")
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    def test_assign_default_isolation_segment(self):
        self.client.patch.return_value = self.mock_response(
            "/v3/organizations/organization_id/relationships/default_isolation_segment",
            HTTPStatus.OK,
            None,
            "v3",
            "organizations",
            "PATCH_{id}_relationships_default_isolation_segment_response.json",
        )
        result = self.client.v3.organizations.assign_default_isolation_segment("organization_id", "iso_seg_guid")
        self.client.patch.assert_called_with(self.client.patch.return_value.url, json={"data": {"guid": "iso_seg_guid"}})
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ToOneRelationship)
        self.assertEqual(result.guid, "9d8e007c-ce52-4ea7-8a57-f2825d2c6b39")

    def test_get_default_isolation_segment(self):
        self.client.get.return_value = self.mock_response(
            "/v3/organizations/organization_id/relationships/default_isolation_segment",
            HTTPStatus.OK,
            None,
            "v3",
            "organizations",
            "GET_{id}_relationships_default_isolation_segment_response.json",
        )

        result = self.client.v3.organizations.get_default_isolation_segment("organization_id")

        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsInstance(result, ToOneRelationship)
        self.assertEqual(result.guid, "9d8e007c-ce52-4ea7-8a57-f2825d2c6b39")

    def test_get_default_domain(self):
        self.client.get.return_value = self.mock_response(
            "/v3/organizations/organization_id/domains/default",
            HTTPStatus.OK,
            None,
            "v3",
            "organizations",
            "GET_{id}_default_domain_response.json",
        )
        default_domain = self.client.v3.organizations.get_default_domain("organization_id")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual("test-domain.com", default_domain["name"])
        self.assertIsInstance(default_domain, Entity)

    def test_get_usage_summary(self):
        self.client.get.return_value = self.mock_response(
            "/v3/organizations/organization_id/usage_summary",
            HTTPStatus.OK,
            None,
            "v3",
            "organizations",
            "GET_{id}_usage_summary_response.json",
        )
        self.client.v3.organizations.get_usage_summary("organization_id")
        self.client.get.assert_called_with(self.client.get.return_value.url)

    @patch.object(sys, "argv", ["main", "list_organizations"])
    def test_main_list_organizations(self):
        with patch("cloudfoundry_client.main.main.build_client_from_configuration", new=lambda: self.client):
            self.client.get.return_value = self.mock_response(
                "/v3/organizations", HTTPStatus.OK, None, "v3", "organizations", "GET_response.json"
            )
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)

    @patch.object(sys, "argv", ["main", "get_organization", "24637893-3b77-489d-bb79-8466f0d88b52"])
    def test_main_get_organizations(self):
        with patch("cloudfoundry_client.main.main.build_client_from_configuration", new=lambda: self.client):
            self.client.get.return_value = self.mock_response(
                "/v3/organizations/24637893-3b77-489d-bb79-8466f0d88b52",
                HTTPStatus.OK,
                None,
                "v3",
                "organizations",
                "GET_{id}_response.json",
            )
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)
