import sys
from unittest import TestCase
from unittest.mock import patch, MagicMock

import cloudfoundry_client.main.main as main
from abstract_test_case import AbstractTestCase
from cloudfoundry_client.operations.push.push import PushOperation
from fake_requests import get_fixtures_path


class TestPushOperation(TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_split_route_with_port_and_path(self):
        domain, port, path = PushOperation._split_route(dict(route='foo-((suffix)).apps.internal:666/some/path'))
        self.assertEqual('foo-((suffix)).apps.internal', domain)
        self.assertEqual(666, port)
        self.assertEqual('/some/path', path)

    def test_split_route_without_port_and_path(self):
        domain, port, path = PushOperation._split_route(dict(route='foo-((suffix)).apps.internal'))
        self.assertEqual('foo-((suffix)).apps.internal', domain)
        self.assertIsNone(port)
        self.assertEqual('', path)

    def test_split_route_without_port_path(self):
        domain, port, path = PushOperation._split_route(dict(route='foo-((suffix)).apps.internal/path'))
        self.assertEqual('foo-((suffix)).apps.internal', domain)
        self.assertIsNone(port)
        self.assertEqual('/path', path)

    def test_split_route_without_path(self):
        domain, port, path = PushOperation._split_route(dict(route='foo-((suffix)).apps.internal:666'))
        self.assertEqual('foo-((suffix)).apps.internal', domain)
        self.assertEqual(666, port)
        self.assertEqual('', path)

    def test_to_host_should_remove_unwanted_characters(self):
        host = PushOperation._to_host('idzone-3.0.7-rec-tb1_bobby')
        self.assertEquals('idzone-307-rec-tb1-bobby', host)

    @patch.object(sys, 'argv', ['main', 'push_app', get_fixtures_path('fake', 'manifest_main.yml'), '-space_guid',
                                'space_id'])
    def test_main_push(self):
        class FakeOperation(object):
            def __init__(self):
                self.push = MagicMock()

        client = object()
        push_operation = FakeOperation()
        with patch('cloudfoundry_client.main.main.build_client_from_configuration',
                   new=lambda: client), \
             patch('cloudfoundry_client.main.operation_commands.PushOperation', new=lambda c: push_operation):
            main.main()
            push_operation.push.assert_called_with('space_id', get_fixtures_path('fake', 'manifest_main.yml'))
