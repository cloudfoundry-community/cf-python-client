import sys
import unittest

import cloudfoundry_client.main.main as main
from abstract_test_case import AbstractTestCase
from cloudfoundry_client.errors import InvalidStatusCode
from cloudfoundry_client.imported import BAD_REQUEST, OK, reduce
from fake_requests import mock_response, TARGET_ENDPOINT
from imported import CREATED, patch, call, NO_CONTENT


class TestApps(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = mock_response('/v2/apps',
                                                     OK,
                                                     None,
                                                     'v2', 'apps', 'GET_response.json')
        all_applications = [application for application in self.client.v2.apps.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(len(all_applications), 3)
        print('test_list - Application - %s' % str(all_applications[0]))
        self.assertEqual(all_applications[0]['entity']['name'], "name-423")

    def test_list_filtered(self):
        self.client.get.return_value = mock_response(
            '/v2/apps?q=name%3Aapplication_name&results-per-page=1&q=space_guid%3Aspace_guid',
            OK,
            None,
            'v2', 'apps', 'GET_space_guid_name_response.json')
        application = self.client.v2.apps.get_first(space_guid='space_guid', name='application_name')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(application)

    def test_get_env(self):
        self.client.get.return_value = mock_response(
            '/v2/apps/app_id/env',
            OK,
            None,
            'v2', 'apps', 'GET_{id}_env_response.json')
        application = self.client.v2.apps.get_env('app_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(application)

    def test_get_instances(self):
        self.client.get.return_value = mock_response(
            '/v2/apps/app_id/instances',
            OK,
            None,
            'v2', 'apps', 'GET_{id}_instances_response.json')
        application = self.client.v2.apps.get_instances('app_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(application)

    def test_get_stats(self):
        self.client.get.return_value = mock_response(
            '/v2/apps/app_id/stats',
            OK,
            None,
            'v2', 'apps', 'GET_{id}_stats_response.json')
        application = self.client.v2.apps.get_stats('app_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(application)

    def test_associate_route(self):
        self.client.put.return_value = mock_response('/v2/apps/app_id/routes/route_id', CREATED, None,
                                                     'v2', 'apps', 'PUT_{id}_routes_{route_id}_response.json')
        self.client.v2.apps.associate_route('app_id', 'route_id')
        self.client.put.assert_called_with(self.client.put.return_value.url, json=None)

    def test_list_routes(self):
        self.client.get.return_value = mock_response(
            '/v2/apps/app_id/routes?q=route_guid%3Aroute_id',
            OK,
            None,
            'v2', 'apps', 'GET_{id}_routes_response.json')
        cpt = reduce(lambda increment, _: increment + 1,
                     self.client.v2.apps.list_routes('app_id', route_guid='route_id'), 0)
        for route in self.client.v2.apps.list_routes('app_id', route_guid='route_id'):
            print(route)
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_remove_route(self):
        self.client.delete.return_value = mock_response('/v2/apps/app_id/routes/route_id', NO_CONTENT, None)
        self.client.v2.apps.remove_route('app_id', 'route_id')
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    def test_list_service_bindings(self):
        self.client.get.return_value = mock_response(
            '/v2/apps/app_id/service_bindings',
            OK,
            None,
            'v2', 'apps', 'GET_{id}_service_bindings_response.json')
        cpt = reduce(lambda increment, _: increment + 1,
                     self.client.v2.apps.list_service_bindings('app_id'), 0)
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get_sumary(self):
        self.client.get.return_value = mock_response(
            '/v2/apps/app_id/summary',
            OK,
            None,
            'v2', 'apps', 'GET_{id}_summary_response.json')
        application = self.client.v2.apps.get_summary('app_id')

        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(application)

    def test_get(self):
        self.client.get.return_value = mock_response(
            '/v2/apps/app_id',
            OK,
            None,
            'v2', 'apps', 'GET_{id}_response.json')
        application = self.client.v2.apps.get('app_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(application)

    def test_start(self):
        self.client.put.return_value = mock_response(
            '/v2/apps/app_id',
            CREATED,
            None,
            'v2', 'apps', 'PUT_{id}_response.json')
        mock_summary = mock_response(
            '/v2/apps/app_id/summary',
            OK,
            None,
            'v2', 'apps', 'GET_{id}_summary_response.json')
        mock_instances_stopped = mock_response(
            '/v2/apps/app_id/instances',
            BAD_REQUEST,
            None,
            'v2', 'apps', 'GET_{id}_instances_stopped_response.json')
        mock_instances_started = mock_response(
            '/v2/apps/app_id/instances',
            OK,
            None,
            'v2', 'apps', 'GET_{id}_instances_response.json')
        self.client.get.side_effect = [mock_summary,
                                       InvalidStatusCode(BAD_REQUEST, dict(code=220001)),
                                       mock_instances_started]

        application = self.client.v2.apps.start('app_id')
        self.client.put.assert_called_with(self.client.put.return_value.url,
                                           json=dict(state='STARTED'))
        self.client.get.assert_has_calls([call(mock_summary.url),
                                          call(mock_instances_stopped.url),
                                          call(mock_instances_started.url)],
                                         any_order=False)
        self.assertIsNotNone(application)

    def test_stop(self):
        self.client.put.return_value = mock_response(
            '/v2/apps/app_id',
            CREATED,
            None,
            'v2', 'apps', 'PUT_{id}_response.json')
        self.client.get.side_effect = [InvalidStatusCode(BAD_REQUEST, dict(code=220001))]
        application = self.client.v2.apps.stop('app_id')
        self.client.put.assert_called_with(self.client.put.return_value.url,
                                           json=dict(state='STOPPED'))
        self.client.get.assert_called_with('%s/v2/apps/app_id/instances' % TARGET_ENDPOINT)
        self.assertIsNotNone(application)

    def test_create(self):
        self.client.post.return_value = mock_response(
            '/v2/apps',
            CREATED,
            None,
            'v2', 'apps', 'POST_response.json')
        application = self.client.v2.apps.create(name='test', space_guid='1fbb3e81-4f55-4fd3-9820-45febbd5e53e',
                                                 stack_guid='82f9c01c-72f2-4d3e-b5ed-eab97a6203cf', memory=1024,
                                                 instances=1,
                                                 disk_quota=1024, health_check_type="port")
        self.client.post.assert_called_with(self.client.post.return_value.url,
                                            json=dict(name='test', space_guid='1fbb3e81-4f55-4fd3-9820-45febbd5e53e',
                                                      stack_guid='82f9c01c-72f2-4d3e-b5ed-eab97a6203cf', memory=1024,
                                                      instances=1, disk_quota=1024, health_check_type="port"))
        self.assertIsNotNone(application)

    def test_update(self):
        self.client.put.return_value = mock_response(
            '/v2/apps/app_id',
            CREATED,
            None,
            'v2', 'apps', 'PUT_{id}_response.json')
        application = self.client.v2.apps.update('app_id', stack_guid='82f9c01c-72f2-4d3e-b5ed-eab97a6203cf',
                                                 memory=1024,
                                                 instances=1, disk_quota=1024, health_check_type="port")
        self.client.put.assert_called_with(self.client.put.return_value.url,
                                           json=dict(stack_guid='82f9c01c-72f2-4d3e-b5ed-eab97a6203cf', memory=1024,
                                                     instances=1, disk_quota=1024, health_check_type="port"))
        self.assertIsNotNone(application)

    def test_remove(self):
        self.client.delete.return_value = mock_response(
            '/v2/apps/app_id',
            NO_CONTENT, None)
        self.client.v2.apps.remove('app_id')
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    def test_restage(self):
        self.client.post.return_value = mock_response(
            '/v2/apps/app_id/restage',
            CREATED,
            None,
            'v2', 'apps', 'POST_{id}_restage_response.json')
        self.client.v2.apps.restage('app_id')
        self.client.post.assert_called_with(self.client.post.return_value.url, json=None)

    def test_entity(self):
        self.client.get.side_effect = [
            mock_response(
                '/v2/apps/app_id',
                OK,
                None,
                'v2', 'apps', 'GET_{id}_response.json'),
            mock_response(
                '/v2/spaces/space_id',
                OK,
                None,
                'v2', 'spaces', 'GET_{id}_response.json')
            ,
            mock_response(
                '/v2/routes',
                OK,
                None,
                'v2', 'routes', 'GET_response.json')
        ]
        application = self.client.v2.apps.get('app_id')

        self.assertIsNotNone(application.space())
        cpt = reduce(lambda increment, _: increment + 1, application.routes(), 0)
        self.assertEqual(cpt, 1)
        self.client.get.assert_has_calls([call(side_effect.url) for side_effect in self.client.get.side_effect],
                                         any_order=False)

    @patch.object(sys, 'argv', ['main', 'list_apps'])
    def test_main_list_apps(self):
        with patch('cloudfoundry_client.main.main.build_client_from_configuration',
                   new=lambda: self.client):
            self.client.get.return_value = mock_response('/v2/apps',
                                                         OK,
                                                         None,
                                                         'v2', 'apps', 'GET_response.json')
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)

    @patch.object(sys, 'argv', ['main', 'delete_app', '906775ea-622e-4bc7-af5d-9aab3b652f81'])
    def test_main_delete_apps(self):
        with patch('cloudfoundry_client.main.main.build_client_from_configuration',
                   new=lambda: self.client):
            self.client.delete.return_value = mock_response('/v2/apps/906775ea-622e-4bc7-af5d-9aab3b652f81',
                                                            NO_CONTENT,
                                                            None)
            main.main()
            self.client.delete.assert_called_with(self.client.delete.return_value.url)

    @patch.object(sys, 'argv', ['main', 'get_app', '906775ea-622e-4bc7-af5d-9aab3b652f81'])
    def test_main_get_app(self):
        with patch('cloudfoundry_client.main.main.build_client_from_configuration',
                   new=lambda: self.client):
            self.client.get.return_value = mock_response('/v2/apps/906775ea-622e-4bc7-af5d-9aab3b652f81',
                                                         OK,
                                                         None,
                                                         'v2', 'apps', 'GET_{id}_response.json')
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)

    @patch.object(sys, 'argv', ['main', 'restage', '906775ea-622e-4bc7-af5d-9aab3b652f81'])
    def test_main_restage_app(self):
        with patch('cloudfoundry_client.main.main.build_client_from_configuration',
                   new=lambda: self.client):
            self.client.post.return_value = mock_response('/v2/apps/906775ea-622e-4bc7-af5d-9aab3b652f81/restage',
                                                          CREATED,
                                                          None,
                                                          'v2', 'apps', 'POST_{id}_restage_response.json')
            main.main()
            self.client.post.assert_called_with(self.client.post.return_value.url, json=None)
