import unittest
from http import HTTPStatus

from abstract_test_case import AbstractTestCase
from fake_requests import mock_response


class TestEvents(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = mock_response('/v2/events?q=type%3Aaudit.route.delete-request',
                                                     HTTPStatus.OK,
                                                     None,
                                                     'v2', 'events', 'GET_response_audit.route.delete-request.json')
        delete_route_events = [event for event in self.client.v2.event.list_by_type('audit.route.delete-request')]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(len(delete_route_events), 1)
        print('test_list - Event - %s' % str(delete_route_events[0]))
        self.assertEqual(delete_route_events[0]['entity']['type'], "audit.route.delete-request")
