import httplib
import unittest

import mock

from cloudfoundry_client.loggregator.loggregator import LoggregatorManager
from fake_requests import mock_response, TARGET_ENDPOINT


class TestLoggregator(unittest.TestCase):
    def setUp(self):
        self.credential_manager = mock.MagicMock()
        self.loggregator = LoggregatorManager(TARGET_ENDPOINT, self.credential_manager)

    def test_recents(self):
        boundary = '7e061f8d6ec00677d6f6b17fcafec9eef2e3a2360e557f72e3e1116efcec'
        self.credential_manager.get.return_value = mock_response('/recent?app=app_id',
                                                                 httplib.OK,
                                                                 {'content-type':
                                                                      'multipart/x-protobuf; boundary=%s' % boundary},
                                                                 'recents', 'GET_response.bin')
        cpt = reduce(lambda increment, _: increment + 1, self.loggregator.get_recent('app_id'), 0)
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url, stream=True)
        self.assertEqual(cpt, 5946)
