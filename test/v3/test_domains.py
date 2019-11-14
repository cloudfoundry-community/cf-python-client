import sys
import unittest
from http import HTTPStatus
from unittest.mock import patch

import cloudfoundry_client.main.main as main
from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.entities import Entity
from fake_requests import mock_response


class TestDomains(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = mock_response('/v3/domains',
                                                     HTTPStatus.OK,
                                                     None,
                                                     'v3', 'domains', 'GET_response.json')
        all_domains = [domain for domain in self.client.v3.domains.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(1, len(all_domains))
        self.assertEqual(all_domains[0]['name'], "test-domain.com")
        self.assertIsInstance(all_domains[0], Entity)

    def test_get(self):
        self.client.get.return_value = mock_response(
            '/v3/domains/domain_id',
            HTTPStatus.OK,
            None,
            'v3', 'domains', 'GET_{id}_response.json')
        result = self.client.v3.domains.get('domain_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)
