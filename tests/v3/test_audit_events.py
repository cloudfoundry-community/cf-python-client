import unittest
from http import HTTPStatus

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.entities import Entity


class TestAuditEvents(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = self.mock_response(
            "/v3/audit_events",
            HTTPStatus.OK,
            None,
            "v3", "audit_events", "GET_response.json"
        )
        all_audit_events = [audit_event for audit_event in self.client.v3.audit_events.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(1, len(all_audit_events))
        self.assertEqual(all_audit_events[0]["type"], "audit.app.update")
        self.assertIsInstance(all_audit_events[0], Entity)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v3/audit_events/audit-event-id",
            HTTPStatus.OK,
            None,
            "v3", "audit_events", "GET_{id}_response.json"
        )
        result = self.client.v3.audit_events.get("audit-event-id")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)
