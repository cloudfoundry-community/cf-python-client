import unittest
from http import HTTPStatus
from unittest.mock import patch, call
from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.jobs import JobTimeout


class TestJobs(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v3/jobs/job_id",
            HTTPStatus.OK,
            None,
            "v3",
            "jobs",
            "GET_{id}_processing_response.json",
        )
        job = self.client.v3.jobs.get("job_id")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(job)

    @patch("time.sleep", return_value=None)
    def test_wait_for_job_completion(self, sleepmock):
        self.client.get.side_effect = [
            self.mock_response(
                "/v3/jobs/job_id",
                HTTPStatus.OK,
                None,
                "v3",
                "jobs",
                "GET_{id}_processing_response.json",
            ),
            self.mock_response(
                "/v3/jobs/job_id",
                HTTPStatus.OK,
                None,
                "v3",
                "jobs",
                "GET_{id}_processing_response.json",
            ),
            self.mock_response(
                "/v3/jobs/job_id",
                HTTPStatus.OK,
                None,
                "v3",
                "jobs",
                "GET_{id}_complete_response.json",
            ),
        ]

        job = self.client.v3.jobs.wait_for_job_completion("job_id")

        assert self.client.get.call_count == 3
        self.assertIsNotNone(job)

    def test_wait_for_job_completion_does_exponential_backoff(self):
        self.client.get.side_effect = [
            self.mock_response(
                "/v3/jobs/job_id",
                HTTPStatus.OK,
                None,
                "v3",
                "jobs",
                "GET_{id}_processing_response.json",
            ),
            self.mock_response(
                "/v3/jobs/job_id",
                HTTPStatus.OK,
                None,
                "v3",
                "jobs",
                "GET_{id}_processing_response.json",
            ),
            self.mock_response(
                "/v3/jobs/job_id",
                HTTPStatus.OK,
                None,
                "v3",
                "jobs",
                "GET_{id}_processing_response.json",
            ),
            self.mock_response(
                "/v3/jobs/job_id",
                HTTPStatus.OK,
                None,
                "v3",
                "jobs",
                "GET_{id}_complete_response.json",
            ),
        ]

        with patch("time.sleep", return_value=None) as m:
            self.client.v3.jobs.wait_for_job_completion("job_id")
            m.assert_has_calls([call(1), call(2), call(4)])

    @patch("time.sleep", return_value=None)
    def test_wait_for_job_completion_has_timeout(self, sleepmock):
        self.client.get.return_value = self.mock_response(
            "/v3/jobs/job_id",
            HTTPStatus.OK,
            None,
            "v3",
            "jobs",
            "GET_{id}_processing_response.json",
        )

        with self.assertRaises(JobTimeout):
            self.client.v3.jobs.wait_for_job_completion("job_id", timeout=0.0001)
