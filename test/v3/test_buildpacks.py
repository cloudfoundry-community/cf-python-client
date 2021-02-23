import sys
import unittest
from http import HTTPStatus
from unittest.mock import patch, mock_open

import cloudfoundry_client.main.main as main
from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.entities import Entity


class TestBuildpacks(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = self.mock_response(
            "/v3/buildpacks", HTTPStatus.OK, None, "v3", "buildpacks", "GET_response.json"
        )
        all_buildpacks = [buildpack for buildpack in self.client.v3.buildpacks.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(1, len(all_buildpacks))
        self.assertEqual(all_buildpacks[0]["name"], "my-buildpack")
        self.assertIsInstance(all_buildpacks[0], Entity)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            "/v3/buildpacks/buildpack_id", HTTPStatus.OK, None, "v3", "buildpacks", "GET_{id}_response.json"
        )
        result = self.client.v3.buildpacks.get("buildpack_id")
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)

    def test_update(self):
        self.client.patch.return_value = self.mock_response(
            "/v3/buildpacks/buildpack_id", HTTPStatus.OK, None, "v3", "buildpacks", "PATCH_{id}_response.json"
        )
        result = self.client.v3.buildpacks.update("buildpack_id", "ruby_buildpack", enabled=True, position=42, stack="windows64")
        self.client.patch.assert_called_with(
            self.client.patch.return_value.url,
            json={
                "locked": False,
                "name": "ruby_buildpack",
                "enabled": True,
                "position": 42,
                "stack": "windows64",
                "metadata": {"labels": None, "annotations": None},
            },
        )
        self.assertIsNotNone(result)

    def test_create(self):
        self.client.post.return_value = self.mock_response(
            "/v3/buildpacks", HTTPStatus.OK, None, "v3", "buildpacks", "POST_response.json"
        )
        result = self.client.v3.buildpacks.create("ruby_buildpack", enabled=True, position=42, stack="windows64")
        self.client.post.assert_called_with(
            self.client.post.return_value.url,
            files=None,
            json={
                "locked": False,
                "name": "ruby_buildpack",
                "enabled": True,
                "position": 42,
                "stack": "windows64",
                "metadata": {"labels": None, "annotations": None},
            },
        )
        self.assertIsNotNone(result)

    def test_remove(self):
        self.client.delete.return_value = self.mock_response("/v3/buildpacks/buildpack_id", HTTPStatus.NO_CONTENT, None)
        self.client.v3.buildpacks.remove("buildpack_id")
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    @patch.object(sys, "argv", ["main", "list_buildpacks"])
    def test_main_list_buildpacks(self):
        with patch("cloudfoundry_client.main.main.build_client_from_configuration", new=lambda: self.client):
            self.client.get.return_value = self.mock_response(
                "/v3/buildpacks", HTTPStatus.OK, None, "v3", "buildpacks", "GET_response.json"
            )
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)

    @patch.object(sys, "argv", ["main", "get_buildpack", "6e72c33b-dff0-4020-8603-bcd8a4eb05e4"])
    def test_main_get_buildpack(self):
        with patch("cloudfoundry_client.main.main.build_client_from_configuration", new=lambda: self.client):
            self.client.get.return_value = self.mock_response(
                "/v3/buildpacks/6e72c33b-dff0-4020-8603-bcd8a4eb05e4",
                HTTPStatus.OK,
                None,
                "v3",
                "buildpacks",
                "GET_{id}_response.json",
            )
            main.main()
            self.client.get.assert_called_with(self.client.get.return_value.url)

    def test_upload_buildpack(self):
        self.client.post.return_value = self.mock_response(
            "/v3/buildpacks/buildpack_id/upload",
            HTTPStatus.ACCEPTED,
            {"Location": "https://somewhere.org/v3/jobs/job_id"},
            "v3",
            "buildpacks",
            "POST_response.json",
        )

        self.client.get.side_effect = [
            self.mock_response(
                "/v3/jobs/job_id",
                HTTPStatus.OK,
                None,
                "v3",
                "jobs",
                "GET_{id}_complete_response.json",
            ),
            self.mock_response(
                "/v3/buildpacks/buildpack_id",
                HTTPStatus.OK,
                None,
                "v3",
                "buildpacks",
                "GET_{id}_response.json",
            ),
        ]

        with patch("cloudfoundry_client.v3.entities.open", mock_open(read_data="ZipContent")) as m:
            with patch("cloudfoundry_client.v3.jobs.JobManager.wait_for_job_completion") as job_mock:
                result = self.client.v3.buildpacks.upload("buildpack_id", "/path/to/buildpack.zip")

                # Check that we made the post call to upload the buildpack
                self.client.post.assert_called_with(
                    self.client.post.return_value.url, files={"bits": ("/path/to/buildpack.zip", m.return_value)}, json=None
                )
                # Check that we wait for job completion
                job_mock.assert_called_once()
                # We are doing upload->waitForJob->getbuildpack to get a fresh buildpack entity after the job finished
                # We then rewrite the job information into the new buildpack entity since it is missing on get endpoint
                # So check job link and function is also in the returned entity when we waited for the job.
                self.assertIsNotNone(result["links"]["job"])
                self.assertIsNotNone(result.job)

    def test_upload_buildpack_dont_wait_for_job_completion(self):
        self.client.post.return_value = self.mock_response(
            "/v3/buildpacks/buildpack_id/upload",
            HTTPStatus.ACCEPTED,
            {"Location": "https://somewhere.org/v3/jobs/job_guid"},
            "v3",
            "buildpacks",
            "POST_response.json",
        )

        with patch("cloudfoundry_client.v3.entities.open", mock_open(read_data="ZipContent")) as m:
            result = self.client.v3.buildpacks.upload("buildpack_id", "/path/to/buildpack.zip", asynchronous=True)

            self.client.post.assert_called_with(
                self.client.post.return_value.url, files={"bits": ("/path/to/buildpack.zip", m.return_value)}, json=None
            )
            self.client.get.assert_not_called()

        self.assertIsNotNone(result)
