import httplib
import unittest

import mock

from cloudfoundry_client.v2.applications import ApplicationManager
from fake_requests import mock_response, TARGET_ENDPOINT


class TestApplications(unittest.TestCase):
    def setUp(self):
        self.credential_manager = mock.MagicMock()
        self.applications = ApplicationManager(TARGET_ENDPOINT, self.credential_manager)

    def test_list(self):
        self.credential_manager.get.return_value = mock_response('/v2/apps',
                                                                 httplib.OK,
                                                                 'v2', 'apps', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1, self.applications.list(), 0)
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertEqual(cpt, 3)

    def test_list_filtered(self):
        self.credential_manager.get.return_value = mock_response(
            '/v2/apps?q=space_guid%20IN%20space_guid&q=name%20IN%20application_name',
            httplib.OK,
            'v2', 'apps', 'GET_space_guid_name_response.json')
        application = self.applications.get_first(space_guid='space_guid', name='application_name')
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertIsNotNone(application)

    def test_get_env(self):
        self.credential_manager.get.return_value = mock_response(
            '/v2/apps/app_id/env',
            httplib.OK,
            'v2', 'apps', 'GET_{id}_env_response.json')
        application = self.applications.get_env('app_id')
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertIsNotNone(application)

    def test_get_instances(self):
        self.credential_manager.get.return_value = mock_response(
            '/v2/apps/app_id/instances',
            httplib.OK,
            'v2', 'apps', 'GET_{id}_instances_response.json')
        application = self.applications.get_instances('app_id')
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertIsNotNone(application)

    def test_get_stats(self):
        self.credential_manager.get.return_value = mock_response(
            '/v2/apps/app_id/stats',
            httplib.OK,
            'v2', 'apps', 'GET_{id}_stats_response.json')
        application = self.applications.get_stats('app_id')
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertIsNotNone(application)

    def test_get_routes(self):
        self.credential_manager.get.return_value = mock_response(
            '/v2/apps/app_id/routes?q=route_guid%20IN%20route_id',
            httplib.OK,
            'v2', 'apps', 'GET_{id}_routes_response.json')
        cpt = reduce(lambda increment, _: increment + 1,
                     self.applications.list_routes('app_id', route_guid='route_id'), 0)
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.credential_manager.get.return_value = mock_response(
            '/v2/apps/app_id',
            httplib.OK,
            'v2', 'apps', 'GET_{id}_response.json')
        application = self.applications.get('app_id')
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertIsNotNone(application)

    def test_start(self):
        self.credential_manager.put.return_value = mock_response(
            '/v2/apps/app_id',
            httplib.CREATED,
            'v2', 'apps', 'PUT_{id}_response.json')
        self.credential_manager.get.return_value = mock_response(
            '/v2/apps/app_id/instances',
            httplib.OK,
            'v2', 'apps', 'GET_{id}_instances_response.json')

        application = self.applications.start('app_id')
        self.credential_manager.put.assert_called_with(self.credential_manager.put.return_value.url,
                                                       json=dict(state='STARTED'))
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertIsNotNone(application)

    def test_stop(self):
        self.credential_manager.put.return_value = mock_response(
            '/v2/apps/app_id',
            httplib.CREATED,
            'v2', 'apps', 'PUT_{id}_response.json')
        self.credential_manager.get.return_value = mock_response(
            '/v2/apps/app_id/instances',
            httplib.BAD_REQUEST)

        application = self.applications.stop('app_id')
        self.credential_manager.put.assert_called_with(self.credential_manager.put.return_value.url,
                                                       json=dict(state='STOPPED'))
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertIsNotNone(application)
