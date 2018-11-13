import unittest

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.imported import OK
from cloudfoundry_client.v3.entities import Entity
from fake_requests import mock_response
from imported import call, NO_CONTENT


class TestApps(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = mock_response('/v3/apps',
                                                     OK,
                                                     None,
                                                     'v3', 'apps', 'GET_response.json')
        all_applications = [application for application in self.client.v3.apps.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_applications))
        self.assertEqual(all_applications[0]['name'], "my_app")
        self.assertIsInstance(all_applications[0], Entity)

    def test_get(self):
        self.client.get.return_value = mock_response('/v3/apps/app_id',
                                                     OK,
                                                     None,
                                                     'v3', 'apps', 'GET_{id}_response.json')
        application = self.client.v3.apps.get('app_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual("my_app", application['name'])
        self.assertIsInstance(application, Entity)

    def test_get_then_space(self):
        get_app = mock_response('/v3/apps/app_id', OK, None, 'v3', 'apps', 'GET_{id}_response.json')
        get_space = mock_response('/v3/spaces/2f35885d-0c9d-4423-83ad-fd05066f8576', OK, None,
                                  'v3', 'spaces', 'GET_{id}_response.json')
        self.client.get.side_effect = [
            get_app,
            get_space
        ]
        space = self.client.v3.apps.get('app_id').space()
        # self.client.get.assert_has_calls([call(get_app.url),
        #                                   call(get_space.url)],
        #                                  any_order=False)
        self.assertEqual("my-space", space['name'])

    def test_get_then_start(self):
        self.client.get.return_value = mock_response('/v3/apps/app_id', OK, None,
                                                     'v3', 'apps', 'GET_{id}_response.json')
        self.client.post.return_value =  mock_response('/v3/apps/app_id/actions/start', OK, None,
                                                       'v3', 'apps', 'POST_{id}_actions_start_response.json')

        app = self.client.v3.apps.get('app_id').start()
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.client.post.assert_called_with(self.client.post.return_value.url, json=None)
        self.assertEqual("my_app", app['name'])
        self.assertIsInstance(app, Entity)

    def test_remove(self):
        self.client.delete.return_value = mock_response(
            '/v3/apps/app_id', NO_CONTENT, None)
        self.client.v3.apps.remove('app_id')
        self.client.delete.assert_called_with(self.client.delete.return_value.url)
