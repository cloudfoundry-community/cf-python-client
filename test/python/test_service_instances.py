import httplib
import unittest

import mock

from abstract_test_case import AbstractTestCase
from fake_requests import mock_response


class TestServiceInstances(unittest.TestCase, AbstractTestCase):
    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = mock_response(
            '/v2/service_instances?q=space_guid%20IN%20space_guid&q=service_plan_guid%20IN%20plan_id',
            httplib.OK,
            None,
            'v2', 'service_instances', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1,
                     self.client.service_instance.list(space_guid='space_guid', service_plan_guid='plan_id'), 0)
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.client.get.return_value = mock_response(
            '/v2/service_instances/instance_id',
            httplib.OK,
            None,
            'v2', 'service_instances', 'GET_{id}_response.json')
        result = self.client.service_instance.get('instance_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)

    def test_create(self):
        self.client.post.return_value = mock_response(
            '/v2/service_instances',
            httplib.CREATED,
            None,
            'v2', 'service_instances', 'POST_response.json')
        service_instance = self.client.service_instance.create('space_guid', 'name', 'plan_id',
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
            httplib.OK,
            None,
            'v2', 'service_instances', 'PUT_{id}_response.json')
        service_instance = self.client.service_instance.update('instance_id', instance_name='new-name', tags=['other-tag'])
        self.client.put.assert_called_with(self.client.put.return_value.url,
                                                       json=dict(name='new-name',
                                                                 tags=['other-tag']))
        self.assertIsNotNone(service_instance)

    def test_delete(self):
        self.client.delete.return_value = mock_response(
            '/v2/service_instances/instance_id',
            httplib.NO_CONTENT,
            None)
        self.client.service_instance.remove('instance_id')
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    def test_entity(self):
        self.client.get.side_effect = [
            mock_response(
                '/v2/service_instances/instance_id',
                httplib.OK,
                None,
                'v2', 'service_instances', 'GET_{id}_response.json'),
            mock_response(
                '/v2/spaces/e3138257-8035-4c03-8aba-ab5d35eec0f9',
                httplib.OK,
                None,
                'v2', 'spaces', 'GET_{id}_response.json')
            ,
            mock_response(
                '/v2/service_instances/df52420f-d5b9-4b86-a7d3-6d7005d1ce96/service_bindings',
                httplib.OK,
                None,
                'v2', 'service_bindings', 'GET_response.json'),
            mock_response(
                '/v2/service_plans/65740f84-214a-46cf-b8e3-2233d580f293',
                httplib.OK,
                None,
                'v2', 'service_plans', 'GET_{id}_response.json'),
            mock_response(
                '/v2/service_instances/df52420f-d5b9-4b86-a7d3-6d7005d1ce96/routes',
                httplib.OK,
                None,
                'v2', 'routes', 'GET_response.json'
            )
        ]
        service_instance = self.client.service_instance.get('instance_id')

        self.assertIsNotNone(service_instance.space())
        cpt = reduce(lambda increment, _: increment + 1, service_instance.service_bindings(), 0)
        self.assertEqual(cpt, 1)
        self.assertIsNotNone(service_instance.service_plan())
        cpt = reduce(lambda increment, _: increment + 1, service_instance.routes(), 0)
        self.assertEqual(cpt, 1)
        self.client.get.assert_has_calls([mock.call(side_effect.url) for side_effect in self.client.get.side_effect],
                                         any_order=False)

