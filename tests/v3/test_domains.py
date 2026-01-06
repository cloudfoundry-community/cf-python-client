import sys
import unittest
from http import HTTPStatus
from unittest.mock import patch

import cloudfoundry_client.main.main as main
from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.domains import Domain
from cloudfoundry_client.v3.entities import Entity, ToManyRelationship, ToOneRelationship


class TestDomains(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = self.mock_response(
            "/v3/domains", HTTPStatus.OK, None, "v3", "domains", "GET_response.json"
        )
        all_domains = [domain for domain in self.client.v3.domains.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(1, len(all_domains))
        self.assertEqual(all_domains[0]["name"], "test-domain.com")
        self.assertIsInstance(all_domains[0], Entity)
        for domain in all_domains:
            self.assertIsInstance(domain, Domain)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v3/domains/domain_id", HTTPStatus.OK, None, "v3", "domains", "GET_{id}_response.json"
        )
        result = self.client.v3.domains.get("domain_id")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Domain)

    def test_update(self):
        self.client.patch.return_value = self.mock_response(
            "/v3/domains/domain_id", HTTPStatus.OK, None, "v3", "domains", "PATCH_{id}_response.json"
        )
        result = self.client.v3.domains.update("domain_id")
        self.client.patch.assert_called_with(
            self.client.patch.return_value.url, json={"metadata": {"labels": None, "annotations": None}}
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Domain)

    def test_create(self):
        self.client.post.return_value = self.mock_response(
            "/v3/domains", HTTPStatus.OK, None, "v3", "domains", "POST_response.json"
        )
        result = self.client.v3.domains.create(
            "domain_id",
            internal=False,
            organization=ToOneRelationship("organization-guid"),
            shared_organizations=ToManyRelationship("other-org-guid-1", "other-org-guid-2"),
            meta_labels=None,
            meta_annotations=None,
        )
        self.client.post.assert_called_with(
            self.client.post.return_value.url,
            files=None,
            json={
                "name": "domain_id",
                "internal": False,
                "relationships": {
                    "organization": {"data": {"guid": "organization-guid"}},
                    "shared_organizations": {
                        "data": [
                            {"guid": "other-org-guid-1"},
                            {"guid": "other-org-guid-2"},
                        ]
                    },
                },
            },
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Domain)

    def test_remove(self):
        self.client.delete.return_value = self.mock_response("/v3/domains/domain_id", HTTPStatus.NO_CONTENT, None)
        self.client.v3.domains.remove("domain_id")
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    def test_list_domains_for_org(self):
        self.client.get.return_value = self.mock_response(
            "/v3/organizations/org_id/domains", HTTPStatus.OK, None, "v3", "domains", "GET_response.json"
        )
        all_domains = [domain for domain in self.client.v3.domains.list_domains_for_org("org_id")]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(1, len(all_domains))
        self.assertEqual(all_domains[0]["name"], "test-domain.com")
        for domain in all_domains:
            self.assertIsInstance(domain, Domain)

    def test_share_domain(self):
        self.client.post.return_value = self.mock_response(
            "/v3/domains/domain_id/relationships/shared_organizations",
            HTTPStatus.CREATED,
            None,
            "v3",
            "domains",
            "POST_{id}_relationships_shared_organizations_response.json",
        )
        result = self.client.v3.domains.share_domain(
            "domain_id", ToManyRelationship("organization-guid-1", "organization-guid-2")
        )
        self.client.post.assert_called_with(
            self.client.post.return_value.url,
            files=None,
            json={"data": [{"guid": "organization-guid-1"}, {"guid": "organization-guid-2"}]},
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ToManyRelationship)
        result.guids[0] = "organization-guid-1"
        result.guids[1] = "organization-guid-1"

    def test_unshare_domain(self):
        self.client.delete.return_value = self.mock_response(
            "/v3/domains/domain_id/relationships/shared_organizations/org_id", HTTPStatus.NO_CONTENT, None
        )
        self.client.v3.domains.unshare_domain("domain_id", "org_id")
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    @patch.object(sys, "argv", ["main", "list_domains"])
    def test_main_list_domains(self):
        with patch("cloudfoundry_client.main.main.build_client_from_configuration", new=lambda: self.client):
            self.client.get.return_value = self.mock_response(
                "/v3/domains", HTTPStatus.OK, None, "v3", "domains", "GET_response.json"
            )
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)

    @patch.object(sys, "argv", ["main", "get_domain", "3a5d3d89-3f89-4f05-8188-8a2b298c79d5"])
    def test_main_get_domain(self):
        with patch("cloudfoundry_client.main.main.build_client_from_configuration", new=lambda: self.client):
            self.client.get.return_value = self.mock_response(
                "/v3/domains/3a5d3d89-3f89-4f05-8188-8a2b298c79d5", HTTPStatus.OK, None, "v3", "domains", "GET_{id}_response.json"
            )
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)
