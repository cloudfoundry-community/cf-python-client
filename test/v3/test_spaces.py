import unittest

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.imported import OK
from cloudfoundry_client.v3.entities import Entity
from fake_requests import mock_response
from imported import call, NO_CONTENT


class TestSpaces(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = mock_response('/v3/spaces',
                                                     OK,
                                                     None,
                                                     'v3', 'spaces', 'GET_response.json')
        all_spaces = [space for space in self.client.v3.spaces.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_spaces))
        self.assertEqual(all_spaces[0]['name'], "space1")
        self.assertIsInstance(all_spaces[0], Entity)

    def test_get(self):
        self.client.get.return_value = mock_response('/v3/spaces/space_id',
                                                     OK,
                                                     None,
                                                     'v3', 'spaces', 'GET_{id}_response.json')
        space = self.client.v3.spaces.get('space_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual("my-space", space['name'])
        self.assertIsInstance(space, Entity)

    def test_get_then_space(self):
        get_space = mock_response('/v3/spaces/space_id', OK, None,
                                  'v3', 'spaces', 'GET_{id}_response.json')
        get_organization = mock_response('/v3/organizations/e00705b9-7b42-4561-ae97-2520399d2133', OK, None,
                                         'v3', 'organizations', 'GET_{id}_response.json')
        self.client.get.side_effect = [
            get_space,
            get_organization
        ]
        organization = self.client.v3.spaces.get('space_id').organization()
        self.client.get.assert_has_calls([call(get_space.url),
                                          call(get_organization.url)],
                                         any_order=False)
        self.assertEqual("my-organization", organization['name'])

