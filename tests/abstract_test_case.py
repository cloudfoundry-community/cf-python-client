import json
import os
from http import HTTPStatus
from unittest.mock import MagicMock, patch

from oauth2_client.credentials_manager import CredentialManager

from cloudfoundry_client.client import CloudFoundryClient
from fake_requests import MockResponse


def mock_cloudfoundry_client_class():
    if not getattr(CloudFoundryClient, "CLASS_MOCKED", False):
        mocked_attributes = ["get", "post", "patch", "put", "delete"]

        class MockClass(CredentialManager):
            def __init__(self, *args, **kwargs):
                super(MockClass, self).__init__(*args, **kwargs)
                for attribute in mocked_attributes:
                    setattr(self, attribute, MagicMock())

        CloudFoundryClient.__bases__ = (MockClass,)
        setattr(CloudFoundryClient, "CLASS_MOCKED", True)


class AbstractTestCase(object):
    TARGET_ENDPOINT = "http://somewhere.org"
    AUTHORIZATION_ENDPOINT = "http://login.somewhere.org"
    TOKEN_ENDPOINT = "http://token.somewhere.org"
    DOPPLER_ENDPOINT = "wss://doppler.nd-cfapi.itn.ftgroup:443"
    LOG_STREAM_ENDPOINT = "https://log-stream.nd-cfapi.itn.ftgroup"

    @classmethod
    def mock_client_class(cls):
        mock_cloudfoundry_client_class()

    def build_client(self):
        with patch("cloudfoundry_client.client.requests") as fake_requests:
            self._mock_info_calls(fake_requests)
            self.client = CloudFoundryClient(self.TARGET_ENDPOINT)

    @staticmethod
    def _mock_info_calls(
            requests,
            with_doppler: bool = True,
            with_log_streams: bool = True,
            with_v2: bool = True,
            with_v3: bool = True
    ):
        links = {
            "self": dict(href=AbstractTestCase.TARGET_ENDPOINT),
            "cloud_controller_v2": dict(
                href="%s/v2" % AbstractTestCase.TARGET_ENDPOINT,
                meta=dict(version="2.141.0"),
            ),
            "cloud_controller_v3": dict(
                href="%s/v3" % AbstractTestCase.TARGET_ENDPOINT,
                meta=dict(version="3.76.0"),
            ),
            "logging": dict(href=AbstractTestCase.DOPPLER_ENDPOINT) if with_doppler else None,
            "log_stream": dict(href=AbstractTestCase.LOG_STREAM_ENDPOINT) if with_log_streams else None,
            "app_ssh": dict(href="ssh.nd-cfapi.itn.ftgroup:80"),
            "uaa": dict(href="https://uaa.nd-cfapi.itn.ftgroup"),
            "login": dict(href=AbstractTestCase.AUTHORIZATION_ENDPOINT),
            "network_policy_v0": dict(href="https://api.nd-cfapi.itn.ftgroup/networking/v0/external"),
            "network_policy_v1": dict(href="https://api.nd-cfapi.itn.ftgroup/networking/v1/external"),
        }
        if not with_v2:
            del links["cloud_controller_v2"]
        if not with_v3:
            del links["cloud_controller_v3"]
        requests.get.side_effect = [
            MockResponse(
                "%s/" % AbstractTestCase.TARGET_ENDPOINT,
                status_code=HTTPStatus.OK.value,
                text=json.dumps(dict(links=links)),
            ),
        ]

    @staticmethod
    def get_fixtures_path(*paths):
        return os.path.join(os.path.dirname(__file__), "fixtures", *paths)

    @staticmethod
    def mock_response(uri: str, status_code: HTTPStatus, headers: dict | None, *path_parts: str):
        if len(path_parts) > 0:
            file_name = path_parts[len(path_parts) - 1]
            extension_idx = file_name.rfind(".")
            binary_file = extension_idx >= 0 and file_name[extension_idx:] == ".bin"
            with (open(AbstractTestCase.get_fixtures_path(*path_parts), "rb" if binary_file else "r")) as f:
                return MockResponse(
                    url="%s%s" % (AbstractTestCase.TARGET_ENDPOINT, uri),
                    status_code=status_code.value,
                    text=f.read(),
                    headers=headers,
                )
        else:
            return MockResponse("%s%s" % (AbstractTestCase.TARGET_ENDPOINT, uri), status_code.value, "", headers)
