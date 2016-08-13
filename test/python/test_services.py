import httplib
import unittest
import mock

from abstract_test_case import AbstractTestCase
from fake_requests import mock_response


class TestServices(unittest.TestCase, AbstractTestCase):
    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = mock_response('/v2/services?q=label%20IN%20some_label',
                                                     httplib.OK,
                                                     None,
                                                     'v2', 'services', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1, self.client.service.list(label='some_label'), 0)
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.client.get.return_value = mock_response(
            '/v2/services/service_id',
            httplib.OK,
            None,
            'v2', 'services', 'GET_{id}_response.json')
        result = self.client.service.get('service_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)

    def test_entity(self):
        self.client.get.side_effect = [
            mock_response(
                '/v2/services/service_id',
                httplib.OK,
                None,
                'v2', 'services', 'GET_{id}_response.json'),
            mock_response(
                '/v2/services/2c883dbb-a726-4ecf-a0b7-d65588897e7f/service_plans',
                httplib.OK,
                None,
                'v2', 'service_plans', 'GET_response.json')

        ]
        service = self.client.service.get('service_id')
        cpt = reduce(lambda increment, _: increment + 1, service.service_plans(), 0)
        self.assertEqual(cpt, 1)
        self.client.get.assert_has_calls([mock.call(side_effect.url) for side_effect in self.client.get.side_effect],
                                         any_order=False)
