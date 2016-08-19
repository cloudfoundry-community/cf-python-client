import json
import types

import mock

from cloudfoundry_client.client import CloudFoundryClient
from fake_requests import TARGET_ENDPOINT, mock_response


def mock_class(clazz):
    if not getattr(clazz, 'CLASS_MOCKED', False):
        true_mother_class = clazz.__bases__

        class MockClass(object):
            def __init__(self, *args, **kwargs):
                for mother_class in true_mother_class:
                    for attribute in dir(mother_class):
                        if isinstance(getattr(mother_class, attribute), types.MethodType):
                            setattr(self, attribute, mock.MagicMock())

        clazz.__bases__ = (MockClass,)
        setattr(clazz, 'CLASS_MOCKED', True)


class AbstractTestCase(object):
    @classmethod
    def mock_client_class(cls):
        mock_class(CloudFoundryClient)

    def build_client(self):
        with mock.patch('cloudfoundry_client.client.requests') as fake_requests:
            fake_info_response = mock_response('/v2/info', 200, None)
            fake_info_response.text = json.dumps(dict(api_version='2.X',
                                                      authorization_endpoint=TARGET_ENDPOINT,
                                                      logging_endpoint=TARGET_ENDPOINT))
            fake_requests.get.return_value = fake_info_response
            self.client = CloudFoundryClient(TARGET_ENDPOINT)
