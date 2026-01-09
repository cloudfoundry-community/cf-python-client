import unittest
from http import HTTPStatus

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.entities import Entity


class TestPackages(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = self.mock_response(
            "/v3/packages",
            HTTPStatus.OK,
            None,
            "v3", "packages", "GET_response.json"
        )
        all_packages = [package for package in self.client.v3.packages.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_packages))
        self.assertEqual(all_packages[0]["type"], "bits")
        for droplet in all_packages:
            self.assertIsInstance(droplet, Entity)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v3/packages/package_id",
            HTTPStatus.OK,
            None,
            "v3", "packages", "GET_{id}_response.json"
        )
        result = self.client.v3.packages.get("package_id")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)

    def test_list_droplets(self):
        self.client.get.return_value = self.mock_response(
            "/v3/packages/package_id/droplets", HTTPStatus.OK, None, "v3", "packages", "GET_{id}_droplets_response.json"
        )
        droplets: list[dict] = [droplet for droplet in self.client.v3.packages.list_droplets("package_id")]
        self.assertEqual(2, len(droplets))
        self.assertEqual(droplets[0]["state"], "STAGED")
