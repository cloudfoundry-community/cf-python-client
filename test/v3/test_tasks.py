import unittest

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.imported import OK
from cloudfoundry_client.v3.entities import Entity
from fake_requests import mock_response
from imported import call, NO_CONTENT, CREATED, ACCEPTED


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



