import unittest
from http import HTTPStatus
from unittest.mock import MagicMock

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.entities import EntityManager, Entity


class TestEntities(unittest.TestCase, AbstractTestCase):
    def test_len(self):
        client = MagicMock()
        client.get.return_value = self.mock_response("/fake/something", HTTPStatus.OK, None, "v3", "apps", "GET_response.json")

        entity_manager = EntityManager(self.TARGET_ENDPOINT, client, "/fake/something")

        cpt = entity_manager.list().total_results

        self.assertEqual(cpt, 3)
        client.get.assert_called_with(client.get.return_value.url)

    def test_entity_manager_is_a_generator(self):
        client = MagicMock()
        client.get.return_value = self.mock_response("/fake/something", HTTPStatus.OK, None, "v3", "apps", "GET_response.json")

        entity_manager = EntityManager(self.TARGET_ENDPOINT, client, "/fake/something")

        self.assertIsNotNone(getattr(entity_manager, "__iter__", None))
        self.assertIsNotNone(getattr(entity_manager.__iter__, "__call__", None))
        generator = entity_manager.__iter__()
        self.assertIsNotNone(getattr(generator, "__next__", None))
        self.assertIsNotNone(getattr(generator.__next__, "__call__", None))

    def test_entity_list_is_a_generator(self):
        client = MagicMock()
        client.get.return_value = self.mock_response("/fake/something", HTTPStatus.OK, None, "v3", "apps", "GET_response.json")
        entity_manager = EntityManager(self.TARGET_ENDPOINT, client, "/fake/something")

        generator = entity_manager.list()

        self.assertIsNotNone(getattr(generator, "__next__", None))
        self.assertIsNotNone(getattr(generator.__next__, "__call__", None))

    def test_elements_are_entities(self):
        client = MagicMock()
        client.get.return_value = self.mock_response("/fake/something", HTTPStatus.OK, None, "v3", "apps", "GET_response.json")
        entity_manager = EntityManager(self.TARGET_ENDPOINT, client, "/fake/something")

        entities_list = entity_manager.list()

        for entity in entities_list:
            self.assertIsInstance(entity, Entity)
