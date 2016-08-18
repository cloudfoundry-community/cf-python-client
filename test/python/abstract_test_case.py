import types

import mock
import json

from cloudfoundry_client.client import CloudFoundryClient, CredentialManager
from fake_requests import TARGET_ENDPOINT, mock_response


class AbstractTestCase(object):

    def build_client(self):
        with mock.patch('cloudfoundry_client.client.requests') as fake_requests:
            class MockCredentail(object):
                def __init__(self, *args, **kwargs):
                    for attribute in dir(CredentialManager):
                        if isinstance(getattr(CredentialManager, attribute), types.MethodType):
                            setattr(self, attribute, mock.MagicMock())
            fake_info_response = mock_response('/v2/info', 200, None)
            fake_info_response.text = json.dumps(dict(api_version='2.X',
                                                      authorization_endpoint=TARGET_ENDPOINT,
                                                      logging_endpoint=TARGET_ENDPOINT))
            fake_requests.get.return_value = fake_info_response

            CloudFoundryClient.__bases__ = (MockCredentail,)
            self.client = CloudFoundryClient(TARGET_ENDPOINT)
