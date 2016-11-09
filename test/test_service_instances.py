import sys
import unittest

import cloudfoundry_client.main as main
from abstract_test_case import AbstractTestCase
from cloudfoundry_client.imported import OK, reduce
from fake_requests import mock_response
from imported import patch, call, CREATED, NO_CONTENT


class TestServiceInstances(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = mock_response(
            '/v2/service_instances?q=service_plan_guid%20IN%20plan_id&q=space_guid%20IN%20space_guid',
            OK,
            None,
            'v2', 'service_instances', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1,
                     self.client.service_instances.list(space_guid='space_guid', service_plan_guid='plan_id'), 0)
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.client.get.return_value = mock_response(
            '/v2/service_instances/instance_id',
            OK,
            None,
            'v2', 'service_instances', 'GET_{id}_response.json')
        result = self.client.service_instances.get('instance_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)

    def test_create(self):
        self.client.post.return_value = mock_response(
            '/v2/service_instances',
            CREATED,
            None,
            'v2', 'service_instances', 'POST_response.json')
        service_instance = self.client.service_instances.create('space_guid', 'name', 'plan_id',
                                                                parameters=dict(the_service_broker="wants this object"),
                                                                tags=['mongodb'])
        self.client.post.assert_called_with(self.client.post.return_value.url,
                                            json=dict(name='name',
                                                      space_guid='space_guid',
                                                      service_plan_guid='plan_id',
                                                      parameters=dict(
                                                          the_service_broker="wants this object"),
                                                      tags=['mongodb'])
                                            )
        self.assertIsNotNone(service_instance)

    def test_update(self):
        self.client.put.return_value = mock_response(
            '/v2/service_instances/instance_id',
            OK,
            None,
            'v2', 'service_instances', 'PUT_{id}_response.json')
        service_instance = self.client.service_instances.update('instance_id', instance_name='new-name',
                                                                tags=['other-tag'])
        self.client.put.assert_called_with(self.client.put.return_value.url,
                                           json=dict(name='new-name',
                                                     tags=['other-tag']))
        self.assertIsNotNone(service_instance)

    def test_delete(self):
        self.client.delete.return_value = mock_response(
            '/v2/service_instances/instance_id',
            NO_CONTENT,
            None)
        self.client.service_instances.remove('instance_id')
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    def test_entity(self):
        self.client.get.side_effect = [
            mock_response(
                '/v2/service_instances/instance_id',
                OK,
                None,
                'v2', 'service_instances', 'GET_{id}_response.json'),
            mock_response(
                '/v2/spaces/e3138257-8035-4c03-8aba-ab5d35eec0f9',
                OK,
                None,
                'v2', 'spaces', 'GET_{id}_response.json')
            ,
            mock_response(
                '/v2/service_instances/df52420f-d5b9-4b86-a7d3-6d7005d1ce96/service_bindings',
                OK,
                None,
                'v2', 'service_bindings', 'GET_response.json'),
            mock_response(
                '/v2/service_plans/65740f84-214a-46cf-b8e3-2233d580f293',
                OK,
                None,
                'v2', 'service_plans', 'GET_{id}_response.json'),
            mock_response(
                '/v2/service_instances/df52420f-d5b9-4b86-a7d3-6d7005d1ce96/routes',
                OK,
                None,
                'v2', 'routes', 'GET_response.json'
            ),
            mock_response(
                '/v2/service_instances/df52420f-d5b9-4b86-a7d3-6d7005d1ce96/service_keys',
                OK,
                None,
                'v2', 'service_keys', 'GET_response.json'
            )
        ]
        service_instance = self.client.service_instances.get('instance_id')

        self.assertIsNotNone(service_instance.space())
        cpt = reduce(lambda increment, _: increment + 1, service_instance.service_bindings(), 0)
        self.assertEqual(cpt, 1)
        self.assertIsNotNone(service_instance.service_plan())
        cpt = reduce(lambda increment, _: increment + 1, service_instance.routes(), 0)
        self.assertEqual(cpt, 1)
        cpt = reduce(lambda increment, _: increment + 1, service_instance.service_keys(), 0)
        self.assertEqual(cpt, 1)
        self.client.get.assert_has_calls([call(side_effect.url) for side_effect in self.client.get.side_effect],
                                         any_order=False)

    @patch.object(sys, 'argv', ['main', 'list_service_instances'])
    def test_main_list_service_instances(self):
        with patch('cloudfoundry_client.main.build_client_from_configuration',
                   new=lambda: self.client):
            self.client.get.return_value = mock_response('/v2/service_instances',
                                                         OK,
                                                         None,
                                                         'v2', 'service_instances', 'GET_response.json')
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)

    @patch.object(sys, 'argv', ['main', 'get_service_instance', 'df52420f-d5b9-4b86-a7d3-6d7005d1ce96'])
    def test_main_get_service_instance(self):
        with patch('cloudfoundry_client.main.build_client_from_configuration',
                   new=lambda: self.client):
            self.client.get.return_value = mock_response('/v2/service_instances/df52420f-d5b9-4b86-a7d3-6d7005d1ce96',
                                                         OK,
                                                         None,
                                                         'v2', 'service_instances', 'GET_{id}_response.json')
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)
