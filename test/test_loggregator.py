import unittest

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.imported import OK, reduce
from fake_requests import mock_response


class TestLoggregator(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_recents(self):
        boundary = '7e061f8d6ec00677d6f6b17fcafec9eef2e3a2360e557f72e3e1116efcec'
        self.client.get.return_value = mock_response('/recent?app=app_id',
                                                     OK,
                                                     {'content-type':
                                                          'multipart/x-protobuf; boundary=%s' % boundary},
                                                     'recents', 'GET_response.bin')
        cpt = reduce(lambda increment, _: increment + 1, self.client.loggregator.get_recent('app_id'), 0)
        self.client.get.assert_called_with(self.client.get.return_value.url, stream=True)
        self.assertEqual(cpt, 5946)
