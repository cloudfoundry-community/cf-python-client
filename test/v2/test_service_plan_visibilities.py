import json
import sys
import unittest

import cloudfoundry_client.main.main as main
from abstract_test_case import AbstractTestCase
from cloudfoundry_client.imported import OK, reduce
from fake_requests import mock_response
from imported import patch, CREATED, NO_CONTENT


class TestServicePlanVisibilities(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = mock_response(
            '/v2/service_plan_visibilities?q=space_guid%3Aspace_guid',
            OK,
            None,
            'v2', 'service_plan_visibilities', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1,
                     self.client.v2.service_plan_visibilities.list(space_guid='space_guid'), 0)
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.client.get.return_value = mock_response(
            '/v2/service_plan_visibilities/guid',
            OK,
            None,
            'v2', 'service_plan_visibilities', 'GET_{id}_response.json')
        result = self.client.v2.service_plan_visibilities.get('guid')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)

    def test_create(self):
        self.client.post.return_value = mock_response(
            '/v2/service_plan_visibilities',
            CREATED,
            None,
            'v2', 'service_plan_visibilities', 'POST_response.json')
        service_plan_visibilities = self.client.v2.service_plan_visibilities.create('service_plan_guid',
                                                                                    'organization_guid')
        self.client.post.assert_called_with(self.client.post.return_value.url,
                                            json=dict(service_plan_guid='service_plan_guid',
                                                      organization_guid='organization_guid'))
        self.assertIsNotNone(service_plan_visibilities)

    def test_update(self):
        self.client.put.return_value = mock_response(
            '/v2/service_plan_visibilities/guid',
            OK,
            None,
            'v2', 'service_plan_visibilities', 'PUT_{id}_response.json')
        service_plan_visibilities = \
            self.client.v2.service_plan_visibilities.update('guid',
                                                            service_plan_guid='service_plan_guid',
                                                            organization_guid='organization_guid')
        self.client.put.assert_called_with(self.client.put.return_value.url,
                                           json=dict(service_plan_guid='service_plan_guid',
                                                     organization_guid='organization_guid'))
        self.assertIsNotNone(service_plan_visibilities)

    def test_delete(self):
        self.client.delete.return_value = mock_response(
            '/v2/service_plan_visibilities/guid',
            NO_CONTENT,
            None)
        self.client.v2.service_plan_visibilities.remove('guid')
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    @patch.object(sys, 'argv', ['main', 'create_service_plan_visibility', json.dumps(
        dict(service_plan_guid='service-plan-id',
             organization_guid='organization-id'))])
    def test_main_create_service_plan_visibility(self):
        with patch('cloudfoundry_client.main.main.build_client_from_configuration',
                   new=lambda: self.client):
            self.client.post.return_value = mock_response(
                '/v2/service_plan_visibilities',
                CREATED,
                None,
                'v2', 'service_plan_visibilities', 'POST_response.json')
            main.main()
            self.client.post.assert_called_with(self.client.post.return_value.url,
                                                json=dict(service_plan_guid='service-plan-id',
                                                          organization_guid='organization-id')
                                                )

    @patch.object(sys, 'argv', ['main', 'list_service_plan_visibilities'])
    def test_main_list_service_plan_visibilities(self):
        with patch('cloudfoundry_client.main.main.build_client_from_configuration',
                   new=lambda: self.client):
            self.client.get.return_value = mock_response('/v2/service_plan_visibilities',
                                                         OK,
                                                         None,
                                                         'v2', 'service_plan_visibilities', 'GET_response.json')
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)

    @patch.object(sys, 'argv', ['main', 'get_service_plan_visibility', 'a353104b-1290-418c-bc03-0e647afd0853'])
    def test_main_get_service_plan_visibility(self):
        with patch('cloudfoundry_client.main.main.build_client_from_configuration',
                   new=lambda: self.client):
            self.client.get.return_value = mock_response(
                '/v2/service_plan_visibilities/a353104b-1290-418c-bc03-0e647afd0853',
                OK,
                None,
                'v2', 'service_plan_visibilities', 'GET_{id}_response.json')
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)

    @patch.object(sys, 'argv', ['main', 'delete_service_plan_visibility', '906775ea-622e-4bc7-af5d-9aab3b652f81'])
    def test_main_delete_service_plan_visibility(self):
        with patch('cloudfoundry_client.main.main.build_client_from_configuration',
                   new=lambda: self.client):
            self.client.delete.return_value = mock_response('/v2/service_plan_visibilities/906775ea-622e-4bc7-af5d-9aab3b652f81',
                                                            NO_CONTENT,
                                                            None)
            main.main()
            self.client.delete.assert_called_with(self.client.delete.return_value.url)
