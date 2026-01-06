import unittest
from functools import reduce
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

    def test_list_pagination(self):
        client = MagicMock()

        entity_manager = EntityManager(self.TARGET_ENDPOINT, client, "/fake")
        first_response = self.mock_response(
            "/fake",
            HTTPStatus.OK,
            None,
            "v3", "fake",
            "GET_multi_page_0_response.json",
        )
        second_response = self.mock_response(
            "/fake/last?order-direction=asc&page=2&results-per-page=50",
            HTTPStatus.OK,
            None,
            "v3", "fake",
            "GET_multi_page_1_response.json",
        )

        client.get.side_effect = [first_response, second_response]

        guids = reduce(
            lambda c, entity: c.append(entity["guid"]) or c,
            entity_manager.list(),
            [],
        )
        self.assertEqual(guids, [
            "1cb006ee-fb05-47e1-b541-c34179ddc446",
            "02b4ec9b-94c7-4468-9c23-4e906191a0f8",
            "1cb006ee-fb05-47e1-b541-c34179ddc447",
            "02b4ec9b-94c7-4468-9c23-4e906191a0f9",
        ])
