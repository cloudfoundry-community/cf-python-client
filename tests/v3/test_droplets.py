import unittest
from http import HTTPStatus

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.entities import Entity


class TestDroplets(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_create(self):
        self.client.post.return_value = self.mock_response(
            "/v3/droplets",
            HTTPStatus.OK,
            None,
            "v3", "droplets", "POST_response.json"
        )
        result = self.client.v3.droplets.create(
            app_guid="app-guid",
            process_types={
                "rake": "bundle exec rake",
                "web": "bundle exec rackup config.ru -p $PORT"
            },
            meta_labels={"key": "value"},
            meta_annotations={"note": "detailed information"},
        )
        self.client.post.assert_called_with(
            self.client.post.return_value.url,
            json={
                "relationships": {
                    "app": {
                        "data": {
                            "guid": "app-guid"
                        }
                    }
                },
                "process_types": {
                    "rake": "bundle exec rake",
                    "web": "bundle exec rackup config.ru -p $PORT"
                },
                "metadata": {"labels": {"key": "value"}, "annotations": {"note": "detailed information"}}
            },
            files=None,
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)

    def test_copy(self):
        self.client.post.return_value = self.mock_response(
            "/v3/droplets?source_guid=droplet_id",
            HTTPStatus.OK,
            None,
            "v3", "droplets", "POST_response.json"
        )
        result = self.client.v3.droplets.copy(
            droplet_guid="droplet_id",
            app_guid="app-guid",
            meta_labels={"key": "value"},
            meta_annotations={"note": "detailed information"},
        )
        self.client.post.assert_called_with(
            self.client.post.return_value.url,
            json={
                "relationships": {
                    "app": {
                        "data": {
                            "guid": "app-guid"
                        }
                    }
                },
                "metadata": {"labels": {"key": "value"}, "annotations": {"note": "detailed information"}}
            },
            files=None,
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)

    def test_list(self):
        self.client.get.return_value = self.mock_response(
            "/v3/droplets",
            HTTPStatus.OK,
            None,
            "v3", "droplets", "GET_response.json"
        )
        all_droplets = [droplet for droplet in self.client.v3.droplets.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_droplets))
        self.assertEqual(all_droplets[0]["state"], "STAGED")
        for droplet in all_droplets:
            self.assertIsInstance(droplet, Entity)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v3/droplets/route_id",
            HTTPStatus.OK,
            None,
            "v3", "droplets", "GET_{id}_response.json"
        )
        result = self.client.v3.droplets.get("route_id")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)

    def test_update(self):
        self.client.patch.return_value = self.mock_response(
            "/v3/droplets/droplet_id",
            HTTPStatus.OK,
            None,
            "v3", "droplets", "PATCH_{id}_response.json"
        )
        result = self.client.v3.droplets.update(
            "droplet_id",
            meta_labels={"key": "value"},
            meta_annotations={"note": "detailed information"},
        )
        self.client.patch.assert_called_with(
            self.client.patch.return_value.url,
            json={
                "metadata": {
                    "labels": {"key": "value"},
                    "annotations": {"note": "detailed information"}
                }
            }
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)

    def test_remove(self):
        self.client.delete.return_value = self.mock_response("/v3/droplets/droplet_id", HTTPStatus.NO_CONTENT, None)
        self.client.v3.droplets.remove("droplet_id")
        self.client.delete.assert_called_with(self.client.delete.return_value.url)
