import json
import unittest
from http import HTTPStatus
from unittest.mock import patch
from urllib.parse import quote

from cloudfoundry_client.errors import InvalidStatusCode

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.client import CloudFoundryClient
from fake_requests import MockResponse, MockSession, FakeRequests


class TestCloudfoundryClient(
    unittest.TestCase,
    AbstractTestCase,
):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def test_build_client_when_no_log_stream(self):
        requests = FakeRequests()
        session = MockSession()
        with patch("oauth2_client.credentials_manager.requests", new=requests), patch(
            "cloudfoundry_client.client.requests", new=requests
        ):
            requests.Session.return_value = session
            self._mock_info_calls(requests, with_log_streams=False)
            client = CloudFoundryClient(self.TARGET_ENDPOINT, token_format="opaque")
            self.assertRaises(NotImplementedError, lambda: client.rlpgateway)

    def test_build_client_when_no_doppler(self):
        requests = FakeRequests()
        session = MockSession()
        with patch("oauth2_client.credentials_manager.requests", new=requests), patch(
            "cloudfoundry_client.client.requests", new=requests
        ):
            requests.Session.return_value = session
            self._mock_info_calls(requests, with_doppler=False)
            client = CloudFoundryClient(self.TARGET_ENDPOINT, token_format="opaque")
            self.assertRaises(NotImplementedError, lambda: client.doppler)

    def test_grant_password_request_with_token_format_opaque(self):
        requests = FakeRequests()
        session = MockSession()
        with patch("oauth2_client.credentials_manager.requests", new=requests), patch(
            "cloudfoundry_client.client.requests", new=requests
        ):
            requests.Session.return_value = session
            self._mock_info_calls(requests)
            requests.post.return_value = MockResponse(
                "%s/oauth/token" % self.AUTHORIZATION_ENDPOINT,
                status_code=HTTPStatus.OK.value,
                text=json.dumps(dict(access_token="access-token", refresh_token="refresh-token")),
            )
            client = CloudFoundryClient(self.TARGET_ENDPOINT, token_format="opaque")
            client.init_with_user_credentials("somebody", "p@s$w0rd")
            self.assertEqual("Bearer access-token", session.headers.get("Authorization"))
            requests.post.assert_called_with(
                requests.post.return_value.url,
                data=dict(grant_type="password", username="somebody", scope="", password="p@s$w0rd", token_format="opaque"),
                headers=dict(Accept="application/json", Authorization="Basic Y2Y6"),
                proxies=dict(http="", https=""),
                verify=True,
            )

    def test_refresh_request_with_token_format_opaque(self):
        requests = FakeRequests()
        session = MockSession()
        with patch("oauth2_client.credentials_manager.requests", new=requests), patch(
            "cloudfoundry_client.client.requests", new=requests
        ):
            requests.Session.return_value = session
            self._mock_info_calls(requests)
            requests.post.return_value = MockResponse(
                "%s/oauth/token" % self.AUTHORIZATION_ENDPOINT,
                status_code=HTTPStatus.OK.value,
                text=json.dumps(dict(access_token="access-token", refresh_token="refresh-token")),
            )
            client = CloudFoundryClient(self.TARGET_ENDPOINT, token_format="opaque")
            client.init_with_token("refresh-token")
            self.assertEqual("Bearer access-token", session.headers.get("Authorization"))
            requests.post.assert_called_with(
                requests.post.return_value.url,
                data=dict(grant_type="refresh_token", scope="", refresh_token="refresh-token", token_format="opaque"),
                headers=dict(Accept="application/json", Authorization="Basic Y2Y6"),
                proxies=dict(http="", https=""),
                verify=True,
            )

    def test_grant_password_request_with_login_hint(self):
        requests = FakeRequests()
        session = MockSession()
        with patch("oauth2_client.credentials_manager.requests", new=requests), patch(
            "cloudfoundry_client.client.requests", new=requests
        ):
            requests.Session.return_value = session
            self._mock_info_calls(requests)
            requests.post.return_value = MockResponse(
                "%s/oauth/token" % self.AUTHORIZATION_ENDPOINT,
                status_code=HTTPStatus.OK.value,
                text=json.dumps(dict(access_token="access-token", refresh_token="refresh-token")),
            )
            client = CloudFoundryClient(
                self.TARGET_ENDPOINT, login_hint=quote(json.dumps(dict(origin="uaa"), separators=(",", ":")))
            )
            client.init_with_user_credentials("somebody", "p@s$w0rd")
            self.assertEqual("Bearer access-token", session.headers.get("Authorization"))
            requests.post.assert_called_with(
                requests.post.return_value.url,
                data=dict(
                    grant_type="password",
                    username="somebody",
                    scope="",
                    password="p@s$w0rd",
                    login_hint="%7B%22origin%22%3A%22uaa%22%7D",
                ),
                headers=dict(Accept="application/json", Authorization="Basic Y2Y6"),
                proxies=dict(http="", https=""),
                verify=True,
            )

    def test_get_info(self):
        requests = FakeRequests()
        session = MockSession()
        with patch("oauth2_client.credentials_manager.requests", new=requests), patch(
            "cloudfoundry_client.client.requests", new=requests
        ):
            requests.Session.return_value = session
            self._mock_info_calls(requests)
            info = CloudFoundryClient._get_info(self.TARGET_ENDPOINT)
            self.assertEqual(info.api_endpoint, self.TARGET_ENDPOINT)
            self.assertEqual(info.api_v2_version, self.API_V2_VERSION)
            self.assertEqual(info.doppler_endpoint, self.DOPPLER_ENDPOINT)
            self.assertEqual(info.log_stream_endpoint, self.LOG_STREAM_ENDPOINT)

    def test_invalid_token_v3(self):
        response = MockResponse(
            "http://some-cf-url",
            401,
            text=json.dumps(
                dict(
                    errors=[
                        dict(code=666, title="Some-Error", detail="Error detail"),
                        dict(code=1000, title="CF-InvalidAuthToken", detail="Invalid token"),
                    ]
                )
            ),
        )
        result = CloudFoundryClient._is_token_expired(response)
        self.assertTrue(result)

    def test_invalid_token_v2(self):
        response = MockResponse("http://some-cf-url", 401, text=json.dumps(dict(code=1000, error_code="CF-InvalidAuthToken")))
        result = CloudFoundryClient._is_token_expired(response)
        self.assertTrue(result)

    def test_log_request(self):
        response = MockResponse(
            "http://some-cf-url",
            200,
            text=json.dumps(dict(entity="entityTest", metadata="metadataTest")),
            headers={"x-vcap-request-id": "testVcap"},
        )
        with self.assertLogs(level="DEBUG") as cm:
            CloudFoundryClient._log_request("GET", "testURL", response)
        self.assertEqual(
            cm.output,
            [
                "DEBUG:cloudfoundry_client.client:GET: url=testURL - status_code=200 - vcap-request-id=testVcap - response="
                '{"entity": "entityTest", "metadata": "metadataTest"}'
            ],
        )

    def test_log_request_empty_headers(self):
        response = MockResponse("http://some-cf-url", 200, text=json.dumps(dict(entity="entityTest", metadata="metadataTest")))
        with self.assertLogs(level="DEBUG") as cm:
            CloudFoundryClient._log_request("GET", "testURL", response)
        self.assertEqual(
            cm.output,
            [
                "DEBUG:cloudfoundry_client.client:GET: url=testURL - status_code=200 - vcap-request-id=N/A - response="
                '{"entity": "entityTest", "metadata": "metadataTest"}'
            ],
        )

    def test_check_response_500_without_vcap(self):
        response = MockResponse("http://some-cf-url", 500, text=json.dumps(dict(entity="entityTest", metadata="metadataTest")))
        with self.assertRaises(InvalidStatusCode):
            CloudFoundryClient._check_response(response)

    def test_check_response_500_with_vcap(self):
        response = MockResponse(
            "http://some-cf-url",
            500,
            text=json.dumps(dict(entity="entityTest", metadata="metadataTest")),
            headers={"x-vcap-request-id": "testVcap"},
        )
        with self.assertRaisesRegex(InvalidStatusCode, "testVcap"):
            CloudFoundryClient._check_response(response)

    def test_check_response_500_text(self):
        response = MockResponse("http://some-cf-url", 500, text="This is test text")
        with self.assertRaisesRegex(InvalidStatusCode, "This is test text"):
            CloudFoundryClient._check_response(response)

    def test_check_response_500_json(self):
        response = MockResponse("http://some-cf-url", 500, text=json.dumps(dict(entity="entityTest", metadata="metadataTest")))
        with self.assertRaisesRegex(InvalidStatusCode, "metadataTest"):
            CloudFoundryClient._check_response(response)

    def test_check_response_200(self):
        response = MockResponse("http://some-cf-url", 200, text=json.dumps(dict(entity="entityTest", metadata="metadataTest")))
        self.assertIsNotNone(CloudFoundryClient._check_response(response))
