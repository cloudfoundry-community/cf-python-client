import unittest
from http import HTTPStatus

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.entities import Entity
from cloudfoundry_client.v3.routes import LoadBalancing


class TestRoutes(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_create(self):
        self.client.post.return_value = self.mock_response(
            "/v3/routes",
            HTTPStatus.OK,
            None,
            "v3", "routes", "POST_response.json"
        )
        result = self.client.v3.routes.create(
            space_guid="space-guid",
            domain_guid="domain-guid",
            host="a-hostname",
            path="/some_path",
            port=6666,
            load_balancing=LoadBalancing.ROUND_ROBIN,
            meta_labels={"key": "value"},
            meta_annotations={"note": "detailed information"},
        )
        self.client.post.assert_called_with(
            self.client.post.return_value.url,
            json={
                "host": "a-hostname",
                "path": "/some_path",
                "port": 6666,
                "relationships": {
                    "domain": {
                        "data": {"guid": "domain-guid"}
                    },
                    "space": {
                        "data": {"guid": "space-guid"}
                    }
                },
                "options": {
                    "loadbalancing": "round-robin"
                },
                "metadata": {
                    "labels": {"key": "value"},
                    "annotations": {"note": "detailed information"}
                }
            },
            files=None,
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)

    def test_list(self):
        self.client.get.return_value = self.mock_response(
            "/v3/routes",
            HTTPStatus.OK,
            None,
            "v3", "routes", "GET_response.json"
        )
        all_routes = [route for route in self.client.v3.routes.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(1, len(all_routes))
        self.assertEqual(all_routes[0]["protocol"], "http")
        for route in all_routes:
            self.assertIsInstance(route, Entity)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v3/routes/route_id",
            HTTPStatus.OK,
            None,
            "v3", "routes", "GET_{id}_response.json"
        )
        result = self.client.v3.routes.get("route_id")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)

    def test_update(self):
        self.client.patch.return_value = self.mock_response(
            "/v3/routes/route_id",
            HTTPStatus.OK,
            None,
            "v3", "routes", "PATCH_{id}_response.json"
        )
        result = self.client.v3.routes.update(
            "route_id",
            LoadBalancing.LEAST_CONNECTION,
            meta_labels={"key": "value"},
            meta_annotations={"note": "detailed information"},
        )
        self.client.patch.assert_called_with(
            self.client.patch.return_value.url,
            json={
                "options": {
                    "loadbalancing": "least-connection"
                },
                "metadata": {
                    "labels": {"key": "value"},
                    "annotations": {"note": "detailed information"}
                }
            }
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)

    def test_remove(self):
        self.client.delete.return_value = self.mock_response("/v3/routes/route_id", HTTPStatus.NO_CONTENT, None)
        self.client.v3.routes.remove("route_id")
        self.client.delete.assert_called_with(self.client.delete.return_value.url)
