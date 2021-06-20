import unittest
from http import HTTPStatus

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.processes import Process


class TestProcesses(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = self.mock_response("/v3/processes", HTTPStatus.OK, None, "v3", "processes", "GET_response.json")
        all_processes = [process for process in self.client.v3.processes.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(2, len(all_processes))
        self.assertEqual(all_processes[0]["type"], "web")
        self.assertIsInstance(all_processes[0], Process)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v3/processes/process_id", HTTPStatus.OK, None, "v3", "processes", "GET_{id}_response.json"
        )
        process = self.client.v3.processes.get("process_id")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual("rackup", process["command"])
        self.assertIsInstance(process, Process)

