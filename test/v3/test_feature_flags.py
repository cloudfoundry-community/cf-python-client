import unittest
from http import HTTPStatus

from abstract_test_case import AbstractTestCase
from fake_requests import mock_response


class TestFeatureFlags(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = mock_response('/v3/feature_flags',
                                                     HTTPStatus.OK,
                                                     None,
                                                     'v3', 'feature_flags', 'GET_response.json')
        all_feature_flags = [feature_flag for feature_flag in self.client.v3.feature_flags.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_feature_flags))
        self.assertEqual(all_feature_flags[0]['name'], "my_feature_flag")
        self.assertEqual(all_feature_flags[1]['name'], "my_second_feature_flag")

    def test_get(self):
        self.client.get.return_value = mock_response('/v3/feature_flags/feature_flag_name',
                                                     HTTPStatus.OK,
                                                     None,
                                                     'v3', 'feature_flags', 'GET_{id}_response.json')
        feature_flag = self.client.v3.feature_flags.get('feature_flag_name')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual("my_feature_flag", feature_flag['name'])
