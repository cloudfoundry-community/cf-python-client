import httplib
import unittest

import mock

from abstract_test_case import AbstractTestCase
from fake_requests import mock_response
import mock

class TestSpaces(unittest.TestCase, AbstractTestCase):
    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = mock_response('/v2/spaces?q=organization_guid%20IN%20org_id',
                                                                 httplib.OK,
                                                                 None,
                                                                 'v2', 'spaces', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1, self.client.space.list(organization_guid='org_id'), 0)
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.client.get.return_value = mock_response(
            '/v2/spaces/space_id',
            httplib.OK,
            None,
            'v2', 'spaces', 'GET_{id}_response.json')
        result = self.client.space.get('space_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)

    def test_entity(self):
        self.client.get.side_effect = [
            mock_response(
                '/v2/spaces/space_id',
                httplib.OK,
                None,
                'v2', 'spaces', 'GET_{id}_response.json'),
            mock_response(
                '/v2/organizations/d7d77408-a250-45e3-8de5-71fcf199bbab',
                httplib.OK,
                None,
                'v2', 'organizations', 'GET_{id}_response.json'),
            mock_response(
                '/v2/spaces/2d745a4b-67e3-4398-986e-2adbcf8f7ec9/apps',
                httplib.OK,
                None,
                'v2', 'apps', 'GET_response.json'),
            mock_response(
                '/v2/spaces/2d745a4b-67e3-4398-986e-2adbcf8f7ec9/service_instances',
                httplib.OK,
                None,
                'v2', 'service_instances', 'GET_response.json')
        ]
        space = self.client.space.get('space_id')
        self.assertIsNotNone(space.organization())
        cpt = reduce(lambda increment, _: increment + 1, space.applications(), 0)
        self.assertEqual(cpt, 3)
        cpt = reduce(lambda increment, _: increment + 1, space.service_instances(), 0)
        self.assertEqual(cpt, 1)
        self.client.get.assert_has_calls([mock.call(side_effect.url) for side_effect in self.client.get.side_effect],
                                         any_order=False)

