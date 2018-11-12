import json
import unittest

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.client import CloudFoundryClient
from cloudfoundry_client.imported import OK
from cloudfoundry_client.imported import quote
from fake_requests import MockResponse, MockSession, FakeRequests
from fake_requests import TARGET_ENDPOINT
from imported import patch


class TestCloudfoundryClient(unittest.TestCase, AbstractTestCase,):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()


    def test_grant_password_request_with_token_format_opaque(self):
        requests = FakeRequests()
        session = MockSession()
        with patch('oauth2_client.credentials_manager.requests', new=requests), \
             patch('cloudfoundry_client.client.requests', new=requests):
            requests.Session.return_value = session
            requests.get.return_value = MockResponse('%s/v2/info' % TARGET_ENDPOINT,
                                                     status_code=OK,
                                                     text=json.dumps(dict(api_version='2.1',
                                                                          authorization_endpoint=TARGET_ENDPOINT)))
            requests.post.return_value = MockResponse('%s/oauth/token' % TARGET_ENDPOINT,
                                                      status_code=OK,
                                                      text=json.dumps(dict(access_token='access-token',
                                                                           refresh_token='refresh-token')))
            client = CloudFoundryClient(TARGET_ENDPOINT, token_format='opaque')
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
            requests.get.return_value = MockResponse('%s/v2/info' % TARGET_ENDPOINT,
                                                     status_code=OK,
                                                     text=json.dumps(dict(api_version='2.1',
                                                                          authorization_endpoint=TARGET_ENDPOINT)))
            requests.post.return_value = MockResponse('%s/oauth/token' % TARGET_ENDPOINT,
                                                      status_code=OK,
                                                      text=json.dumps(dict(access_token='access-token',
                                                                           refresh_token='refresh-token')))
            client = CloudFoundryClient(TARGET_ENDPOINT, token_format='opaque')
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
            requests.get.return_value = MockResponse('%s/v2/info' % TARGET_ENDPOINT,
                                                     status_code=OK,
                                                     text=json.dumps(dict(api_version='2.1',
                                                                          authorization_endpoint=TARGET_ENDPOINT)))
            requests.post.return_value = MockResponse('%s/oauth/token' % TARGET_ENDPOINT,
                                                      status_code=OK,
                                                      text=json.dumps(dict(access_token='access-token',
                                                                           refresh_token='refresh-token')))
            client = CloudFoundryClient(TARGET_ENDPOINT, login_hint=quote(json.dumps(dict(origin='uaa'),
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
