import json

from oauth2_client.credentials_manager import CredentialManager

from cloudfoundry_client.client import CloudFoundryClient
from fake_requests import TARGET_ENDPOINT, mock_response
from imported import MagicMock, patch


def mock_cloudfoundry_client_class():
    if not getattr(CloudFoundryClient, 'CLASS_MOCKED', False):
        mocked_attributes = ['get', 'post', 'patch', 'put', 'delete']

        class MockClass(CredentialManager):
            def __init__(self, *args, **kwargs):
                super(MockClass, self).__init__(*args, **kwargs)
                for attribute in mocked_attributes:
                    setattr(self, attribute, MagicMock())

        CloudFoundryClient.__bases__ = (MockClass,)
        setattr(CloudFoundryClient, 'CLASS_MOCKED', True)


class AbstractTestCase(object):
    @classmethod
    def mock_client_class(cls):
        mock_cloudfoundry_client_class()

    def build_client(self):
        with patch('cloudfoundry_client.client.requests') as fake_requests:
            fake_info_response = mock_response('/v2/info', 200, None)
            fake_info_response.text = json.dumps(dict(api_version='2.X',
                                                      authorization_endpoint=TARGET_ENDPOINT))
            fake_requests.get.return_value = fake_info_response
            self.client = CloudFoundryClient(TARGET_ENDPOINT)
