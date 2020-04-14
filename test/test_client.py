import json
import unittest
from http import HTTPStatus
from unittest.mock import patch
from urllib.parse import quote

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.client import CloudFoundryClient
from fake_requests import MockResponse, MockSession, FakeRequests


class TestCloudfoundryClient(unittest.TestCase, AbstractTestCase, ):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def test_build_client_when_no_log_stream(self):
        requests = FakeRequests()
        session = MockSession()
        with patch('oauth2_client.credentials_manager.requests', new=requests), \
             patch('cloudfoundry_client.client.requests', new=requests):
            requests.Session.return_value = session
            self._mock_info_calls(requests, with_log_streams=False)
            client = CloudFoundryClient(self.TARGET_ENDPOINT, token_format='opaque')
            self.assertRaises(NotImplementedError, lambda: client.rlpgateway)

    def test_build_client_when_no_doppler(self):
        requests = FakeRequests()
        session = MockSession()
        with patch('oauth2_client.credentials_manager.requests', new=requests), \
             patch('cloudfoundry_client.client.requests', new=requests):
            requests.Session.return_value = session
            self._mock_info_calls(requests, with_doppler=False)
            client = CloudFoundryClient(self.TARGET_ENDPOINT, token_format='opaque')
            self.assertRaises(NotImplementedError, lambda: client.doppler)

    def test_grant_password_request_with_token_format_opaque(self):
        requests = FakeRequests()
        session = MockSession()
        with patch('oauth2_client.credentials_manager.requests', new=requests), \
             patch('cloudfoundry_client.client.requests', new=requests):
            requests.Session.return_value = session
            self._mock_info_calls(requests)
            requests.post.return_value = MockResponse('%s/oauth/token' % self.TOKEN_ENDPOINT,
                                                      status_code=HTTPStatus.OK.value,
                                                      text=json.dumps(dict(access_token='access-token',
                                                                           refresh_token='refresh-token')))
            client = CloudFoundryClient(self.TARGET_ENDPOINT, token_format='opaque')
            client.init_with_user_credentials('somebody', 'p@s$w0rd')
            self.assertEqual('Bearer access-token', session.headers.get('Authorization'))
            requests.post.assert_called_with(requests.post.return_value.url,
                                             data=dict(grant_type='password',
                                                       username='somebody',
                                                       scope='',
                                                       password='p@s$w0rd',
                                                       token_format='opaque'),
                                             headers=dict(Accept='application/json', Authorization='Basic Y2Y6'),
                                             proxies=dict(http='', https=''),
                                             verify=True)

    def test_refresh_request_with_token_format_opaque(self):
        requests = FakeRequests()
        session = MockSession()
        with patch('oauth2_client.credentials_manager.requests', new=requests), \
             patch('cloudfoundry_client.client.requests', new=requests):
            requests.Session.return_value = session
            self._mock_info_calls(requests)
            requests.post.return_value = MockResponse('%s/oauth/token' % self.TOKEN_ENDPOINT,
                                                      status_code=HTTPStatus.OK.value,
                                                      text=json.dumps(dict(access_token='access-token',
                                                                           refresh_token='refresh-token')))
            client = CloudFoundryClient(self.TARGET_ENDPOINT, token_format='opaque')
            client.init_with_token('refresh-token')
            self.assertEqual('Bearer access-token', session.headers.get('Authorization'))
            requests.post.assert_called_with(requests.post.return_value.url,
                                             data=dict(grant_type='refresh_token',
                                                       scope='',
                                                       refresh_token='refresh-token',
                                                       token_format='opaque'),
                                             headers=dict(Accept='application/json', Authorization='Basic Y2Y6'),
                                             proxies=dict(http='', https=''),
                                             verify=True)

    def test_grant_password_request_with_login_hint(self):
        requests = FakeRequests()
        session = MockSession()
        with patch('oauth2_client.credentials_manager.requests', new=requests), \
             patch('cloudfoundry_client.client.requests', new=requests):
            requests.Session.return_value = session
            self._mock_info_calls(requests)
            requests.post.return_value = MockResponse('%s/oauth/token' % self.TOKEN_ENDPOINT,
                                                      status_code=HTTPStatus.OK.value,
                                                      text=json.dumps(dict(access_token='access-token',
                                                                           refresh_token='refresh-token')))
            client = CloudFoundryClient(self.TARGET_ENDPOINT, login_hint=quote(json.dumps(dict(origin='uaa'),
                                                                                          separators=(',', ':'))))
            client.init_with_user_credentials('somebody', 'p@s$w0rd')
            self.assertEqual('Bearer access-token', session.headers.get('Authorization'))
            requests.post.assert_called_with(requests.post.return_value.url,
                                             data=dict(grant_type='password',
                                                       username='somebody',
                                                       scope='',
                                                       password='p@s$w0rd',
                                                       login_hint='%7B%22origin%22%3A%22uaa%22%7D'),
                                             headers=dict(Accept='application/json', Authorization='Basic Y2Y6'),
                                             proxies=dict(http='', https=''),
                                             verify=True)

    def test_get_info(self):
        requests = FakeRequests()
        session = MockSession()
        with patch('oauth2_client.credentials_manager.requests', new=requests), \
             patch('cloudfoundry_client.client.requests', new=requests):
            requests.Session.return_value = session
            self._mock_info_calls(requests)
            info = CloudFoundryClient._get_info(self.TARGET_ENDPOINT)
            self.assertEqual(info.api_endpoint, self.TARGET_ENDPOINT)
            self.assertEqual(info.api_v2_version, self.API_V2_VERSION)
            self.assertEqual(info.doppler_endpoint, self.DOPPLER_ENDPOINT)
            self.assertEqual(info.log_stream_endpoint, self.LOG_STREAM_ENDPOINT)
