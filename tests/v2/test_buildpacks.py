import unittest
from functools import reduce
from http import HTTPStatus

from abstract_test_case import AbstractTestCase


class TestBuildpacks(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = self.mock_response(
            "/v2/buildpacks", HTTPStatus.OK, None, "v2", "buildpacks", "GET_response.json"
        )
        cpt = reduce(lambda increment, _: increment + 1, self.client.v2.buildpacks.list(), 0)
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(cpt, 3)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v2/buildpacks/buildpack_id", HTTPStatus.OK, None, "v2", "buildpacks", "GET_{id}_response.json"
        )
        result = self.client.v2.buildpacks.get("buildpack_id")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)

    def test_update(self):
        self.client.put.return_value = self.mock_response(
            "/v2/buildpacks/build_pack_id", HTTPStatus.CREATED, None, "v2", "apps", "PUT_{id}_response.json"
        )
        result = self.client.v2.buildpacks.update("build_pack_id", dict(enabled=False))
        self.client.put.assert_called_with(self.client.put.return_value.url, json=dict(enabled=False))
        self.assertIsNotNone(result)
