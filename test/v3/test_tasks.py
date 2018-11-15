import sys
import unittest

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.imported import OK
from cloudfoundry_client.main import main
from cloudfoundry_client.v3.entities import Entity
from fake_requests import mock_response
from imported import patch, CREATED, ACCEPTED


class TestTasks(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = mock_response('/v3/tasks',
                                                     OK,
                                                     None,
                                                     'v3', 'tasks', 'GET_response.json')
        all_tasks = [task for task in self.client.v3.tasks.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_tasks))
        self.assertEqual(all_tasks[0]['name'], "hello")
        self.assertIsInstance(all_tasks[0], Entity)

    def test_get(self):
        self.client.get.return_value = mock_response('/v3/tasks/task_id',
                                                     OK,
                                                     None,
                                                     'v3', 'tasks', 'GET_{id}_response.json')
        task = self.client.v3.tasks.get('task_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual("migrate", task['name'])
        self.assertIsInstance(task, Entity)

    def test_create(self):
        self.client.post.return_value = mock_response(
            '/v3/apps/app_guid/tasks',
            CREATED,
            None,
            'v3', 'tasks', 'POST_response.json')
        task = self.client.v3.tasks.create('app_guid', command='rake db:migrate')
        self.client.post.assert_called_with(self.client.post.return_value.url,
                                            json=dict(command='rake db:migrate')
                                            )
        self.assertIsNotNone(task)

    def test_cancel(self):
        self.client.post.return_value = mock_response(
            '/v3/tasks/task_guid/actions/cancel',
            ACCEPTED,
            None,
            'v3', 'tasks', 'POST_{id}_actions_cancel_response.json')
        task = self.client.v3.tasks.cancel('task_guid')
        self.client.post.assert_called_with(self.client.post.return_value.url, json=None)
        self.assertIsNotNone(task)

    @patch.object(sys, 'argv', ['main', 'list_tasks', '-names', 'task_name'])
    def test_list_tasks(self):
        with patch('cloudfoundry_client.main.main.build_client_from_configuration',
                   new=lambda: self.client):
            self.client.get.return_value = mock_response('/v3/tasks?names=task_name',
                                                         OK,
                                                         None,
                                                         'v3', 'tasks', 'GET_response.json')
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)

    @patch.object(sys, 'argv', ['main', 'create_task', 'app_id', '{"command": "rake db:migrate", "name": "example"}'])
    def test_create_task(self):
        with patch('cloudfoundry_client.main.main.build_client_from_configuration',
                   new=lambda: self.client):
            self.client.post.return_value = mock_response('/v3/apps/app_id/tasks',
                                                          CREATED,
                                                          None,
                                                          'v3', 'tasks', 'POST_response.json')
            main.main()
            self.client.post.assert_called_with(self.client.post.return_value.url,
                                                json=dict(command='rake db:migrate', name='example'))

    @patch.object(sys, 'argv', ['main', 'cancel_task', 'task_id'])
    def test_cancel_task(self):
        with patch('cloudfoundry_client.main.main.build_client_from_configuration',
                   new=lambda: self.client):
            self.client.post.return_value = mock_response('/v3/tasks/task_id/actions/cancel',
                                                          CREATED,
                                                          None,
                                                          'v3', 'tasks', 'POST_{id}_actions_cancel_response.json')
            main.main()
            self.client.post.assert_called_with(self.client.post.return_value.url, json=None)
