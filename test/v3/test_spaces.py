import unittest
from http import HTTPStatus
from unittest.mock import call

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.entities import Entity, ToOneRelationship


class TestSpaces(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_create(self):
        self.client.post.return_value = self.mock_response(
            "/v3/spaces", HTTPStatus.OK, None, "v3", "spaces", "POST_response.json"
        )
        result = self.client.v3.spaces.create("space-name", "organization-guid")
        self.client.post.assert_called_with(
            self.client.post.return_value.url,
            files=None,
            json={"name": "space-name", "relationships": {"organization": {"data": {"guid": "organization-guid"}}}},
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)

    def test_list(self):
        self.client.get.return_value = self.mock_response("/v3/spaces", HTTPStatus.OK, None, "v3", "spaces", "GET_response.json")
        all_spaces = [space for space in self.client.v3.spaces.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_spaces))
        self.assertEqual(all_spaces[0]["name"], "space1")
        self.assertIsInstance(all_spaces[0], Entity)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v3/spaces/space_id", HTTPStatus.OK, None, "v3", "spaces", "GET_{id}_response.json"
        )
        space = self.client.v3.spaces.get("space_id")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual("my-space", space["name"])
        self.assertIsInstance(space, Entity)

    def test_get_then_organization(self):
        get_space = self.mock_response("/v3/spaces/space_id", HTTPStatus.OK, None, "v3", "spaces", "GET_{id}_response.json")
        get_organization = self.mock_response(
            "/v3/organizations/e00705b9-7b42-4561-ae97-2520399d2133",
            HTTPStatus.OK,
            None,
            "v3",
            "organizations",
            "GET_{id}_response.json",
        )
        self.client.get.side_effect = [get_space, get_organization]
        organization = self.client.v3.spaces.get("space_id").organization()
        self.client.get.assert_has_calls([call(get_space.url), call(get_organization.url)], any_order=False)
        self.assertEqual("my-organization", organization["name"])

    def test_get_assigned_isolation_segment(self):
        self.client.get.return_value = self.mock_response(
            "/v3/spaces/space_id/relationships/isolation_segment",
            HTTPStatus.OK,
            None,
            "v3",
            "spaces",
            "GET_{id}_relationships_isolation_segment_response.json",
        )

        result = self.client.v3.spaces.get_assigned_isolation_segment("space_id")

        self.assertIsInstance(result, ToOneRelationship)
        self.assertEqual("e4c91047-3b29-4fda-b7f9-04033e5a9c9f", result.guid)

    def test_assign_isolation_segment(self):
        self.client.patch.return_value = self.mock_response(
            "/v3/spaces/space_id/relationships/isolation_segment",
            HTTPStatus.OK,
            None,
            "v3",
            "spaces",
            "POST_{id}_relationships_isolation_segment_response.json",
        )
        result = self.client.v3.spaces.assign_isolation_segment("space_id", "iso-seg-guid")
        self.client.patch.assert_called_with(self.client.patch.return_value.url, json={"data": {"guid": "iso-seg-guid"}})
        self.assertIsInstance(result, ToOneRelationship)
        self.assertEqual("iso-seg-guid", result.guid)

    def test_remove(self):
        self.client.delete.return_value = self.mock_response("/v3/spaces/space_id", HTTPStatus.NO_CONTENT, None)
        self.client.v3.spaces.remove("space_id")
        self.client.delete.assert_called_with(self.client.delete.return_value.url)
