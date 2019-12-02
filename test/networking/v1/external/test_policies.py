import unittest
from http import HTTPStatus

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.networking.v1.external.policies import PolicyManager
from fake_requests import mock_response


class TestApps(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = mock_response('/networking/v1/external/policies',
                                                     HTTPStatus.OK,
                                                     None,
                                                     'networking', 'v1', 'external', 'policies', 'GET_response.json')
        all_policies = [policy for policy in self.client.networking_v1_external.policies.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_policies))
        self.assertEqual(all_policies[0]['source']['id'], "1081ceac-f5c4-47a8-95e8-88e1e302efb5")
        self.assertEqual(all_policies[0]['destination']['id'], "38f08df0-19df-4439-b4e9-61096d4301ea")
