import sys
import unittest
from http import HTTPStatus
from unittest.mock import patch

import cloudfoundry_client.main.main as main
from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.entities import Entity, ToManyRelationship
from cloudfoundry_client.v3.organization_quotas import AppsQuota, DomainsQuota, RoutesQuota, ServicesQuota


class TestOrganizationQuotas(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = self.mock_response(
            "/v3/organization_quotas", HTTPStatus.OK, None, "v3", "organization_quotas", "GET_response.json"
        )
        all_quotas = [quota for quota in self.client.v3.organization_quotas.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_quotas))
        self.assertEqual(all_quotas[0]["name"], "don-quixote")
        self.assertIsInstance(all_quotas[0], Entity)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v3/organization_quotas/quota-guid", HTTPStatus.OK, None, "v3", "organization_quotas", "GET_{id}_response.json"
        )
        quota = self.client.v3.organization_quotas.get("quota-guid")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual("don-quixote", quota["name"])
        self.assertIsInstance(quota, Entity)

    def test_update(self):
        self.client.patch.return_value = self.mock_response(
            "/v3/organization_quotas/quota_id", HTTPStatus.OK, None, "v3", "organization_quotas", "PATCH_{id}_response.json"
        )
        result = self.client.v3.organization_quotas.update(
            "quota_id",
            "don-quixote",
            apps_quota=AppsQuota(total_memory_in_mb=5120, per_process_memory_in_mb=1024, total_instances=10, per_app_tasks=5),
            services_quota=ServicesQuota(paid_services_allowed=True, total_service_instances=10, total_service_keys=20),
            routes_quota=RoutesQuota(total_routes=8, total_reserved_ports=4),
            domains_quota=DomainsQuota(total_domains=7),
        )
        self.client.patch.assert_called_with(
            self.client.patch.return_value.url,
            json={
                "name": "don-quixote",
                "apps": {"total_memory_in_mb": 5120, "per_process_memory_in_mb": 1024, "total_instances": 10, "per_app_tasks": 5},
                "services": {"paid_services_allowed": True, "total_service_instances": 10, "total_service_keys": 20},
                "routes": {"total_routes": 8, "total_reserved_ports": 4},
                "domains": {"total_domains": 7},
            },
        )
        self.assertIsNotNone(result)

    def test_create(self):
        self.client.post.return_value = self.mock_response(
            "/v3/organization_quotas", HTTPStatus.OK, None, "v3", "organization_quotas", "POST_response.json"
        )
        result = self.client.v3.organization_quotas.create(
            "don-quixote",
            apps_quota=AppsQuota(total_memory_in_mb=5120, per_process_memory_in_mb=1024, total_instances=10, per_app_tasks=5),
            services_quota=ServicesQuota(paid_services_allowed=True, total_service_instances=10, total_service_keys=20),
            routes_quota=RoutesQuota(total_routes=8, total_reserved_ports=4),
            domains_quota=DomainsQuota(total_domains=7),
            assigned_organizations=ToManyRelationship("assigned-org"),
        )
        self.client.post.assert_called_with(
            self.client.post.return_value.url,
            files=None,
            json={
                "name": "don-quixote",
                "apps": {"total_memory_in_mb": 5120, "per_process_memory_in_mb": 1024, "total_instances": 10, "per_app_tasks": 5},
                "services": {"paid_services_allowed": True, "total_service_instances": 10, "total_service_keys": 20},
                "routes": {"total_routes": 8, "total_reserved_ports": 4},
                "domains": {"total_domains": 7},
                "relationships": {"organizations": {"data": [{"guid": "assigned-org"}]}},
            },
        )
        self.assertIsNotNone(result)

    def test_apply_to_organizations(self):
        self.client.post.return_value = self.mock_response(
            "/v3/organization_quotas/quota_id/relationships/organizations",
            HTTPStatus.OK,
            None,
            "v3",
            "organization_quotas",
            "POST_{id}_organizations_response.json",
        )
        result = self.client.v3.organization_quotas.apply_to_organizations(
            "quota_id",
            organizations=ToManyRelationship("org-guid1", "org-guid2"),
        )
        self.client.post.assert_called_with(
            self.client.post.return_value.url, files=None, json={"data": [{"guid": "org-guid1"}, {"guid": "org-guid2"}]}
        )
        self.assertIsInstance(result, ToManyRelationship)
        # Endpoint adds to existing list of orgs so 1 existing + 2 new
        self.assertEqual(3, len(result.guids))
        self.assertIsNotNone(result["links"])

    def test_remove(self):
        self.client.delete.return_value = self.mock_response("/v3/organization_quotas/quota_id", HTTPStatus.NO_CONTENT, None)
        self.client.v3.organization_quotas.remove("quota_id")
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    @patch.object(sys, "argv", ["main", "list_organization_quotas"])
    def test_main_list_organization_quotas(self):
        with patch("cloudfoundry_client.main.main.build_client_from_configuration", new=lambda: self.client):
            self.client.get.return_value = self.mock_response(
                "/v3/organization_quotas", HTTPStatus.OK, None, "v3", "organization_quotas", "GET_response.json"
            )
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)

    @patch.object(sys, "argv", ["main", "get_organization_quota", "1d3bf0ec-5806-43c4-b64e-8364dba1086a"])
    def test_main_get_organization_quotas(self):
        with patch("cloudfoundry_client.main.main.build_client_from_configuration", new=lambda: self.client):
            self.client.get.return_value = self.mock_response(
                "/v3/organization_quotas/1d3bf0ec-5806-43c4-b64e-8364dba1086a",
                HTTPStatus.OK,
                None,
                "v3",
                "organization_quotas",
                "GET_{id}_response.json",
            )
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)
