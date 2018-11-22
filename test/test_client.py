import json
import unittest

from cloudfoundry_client.client import CloudFoundryClient
from cloudfoundry_client.imported import OK
from fake_requests import MockResponse, MockSession
from fake_requests import TARGET_ENDPOINT
from imported import patch


class TestCloudfoundryClient(unittest.TestCase):

    @patch('requests.Session')
    @patch('requests.get')
    @patch('requests.post')
    def test_grant_password_request_with_token_format_opaque(self, mocked_post, mocked_get, mocked_session):
        session = MockSession()
        mocked_session.return_value = session
        mocked_get.return_value = MockResponse('%s/v2/info' % TARGET_ENDPOINT,
                                               status_code=OK,
                                               text=json.dumps(dict(api_version='2.1',
                                                                    authorization_endpoint=TARGET_ENDPOINT)))
        mocked_post.return_value = MockResponse('%s/oauth/token' % TARGET_ENDPOINT,
                                                        status_code=OK,
                                                        text=json.dumps(dict(access_token='access-token',
                                                                             refresh_token='refresh-token')))
        client = CloudFoundryClient(TARGET_ENDPOINT, token_format='opaque')
        client.init_with_user_credentials('somebody', 'p@s$w0rd')
        self.assertEqual('Bearer access-token', session.headers.get('Authorization'))
        mocked_post.assert_called_with(mocked_post.return_value.url,
                                       data=dict(grant_type='password',
                                                 username='somebody',
                                                 scope='',
                                                 password='p@s$w0rd',
                                                 token_format='opaque'),
                                       headers=dict(Accept='application/json', Authorization='Basic Y2Y6'),
                                       proxies=dict(http='', https=''),
                                       verify=True)

    @patch('requests.Session')
    @patch('requests.get')
    @patch('requests.post')
    def test_refresh_request_with_token_format_opaque(self, mocked_post, mocked_get, mocked_session):
        session = MockSession()
        mocked_session.return_value = session
        mocked_get.return_value = MockResponse('%s/v2/info' % TARGET_ENDPOINT,
                                               status_code=OK,
                                               text=json.dumps(dict(api_version='2.1',
                                                                    authorization_endpoint=TARGET_ENDPOINT)))
        mocked_post.return_value = MockResponse('%s/oauth/token' % TARGET_ENDPOINT,
                                                status_code=OK,
                                                text=json.dumps(dict(access_token='access-token',
                                                                     refresh_token='refresh-token')))
        client = CloudFoundryClient(TARGET_ENDPOINT, token_format='opaque')
        client.init_with_token('refresh-token')
        # self.assertEqual('Bearer access-token', session.headers.get('Authorization'))
        mocked_post.assert_called_with(mocked_post.return_value.url,
                                       data=dict(grant_type='refresh_token',
                                                 scope='',
                                                 refresh_token='refresh-token',
                                                 token_format='opaque'),
                                       headers=dict(Accept='application/json', Authorization='Basic Y2Y6'),
                                       proxies=dict(http='', https=''),
                                       verify=True)

    @patch('requests.Session')
    @patch('requests.get')
    @patch('requests.post')
    def test_grant_password_request_with_login_hint(self, mocked_post, mocked_get, mocked_session):
        session = MockSession()
        mocked_session.return_value = session
        mocked_get.return_value = MockResponse('%s/v2/info' % TARGET_ENDPOINT,
                                               status_code=OK,
                                               text=json.dumps(dict(api_version='2.1',
                                                                    authorization_endpoint=TARGET_ENDPOINT)))
        mocked_post.return_value = MockResponse('%s/oauth/token' % TARGET_ENDPOINT,
                                                status_code=OK,
                                                text=json.dumps(dict(access_token='access-token',
                                                                     refresh_token='refresh-token')))
        client = CloudFoundryClient(TARGET_ENDPOINT, login_hint=dict(origin='uaa'))
        client.init_with_user_credentials('somebody', 'p@s$w0rd')
        self.assertEqual('Bearer access-token', session.headers.get('Authorization'))
        mocked_post.assert_called_with(mocked_post.return_value.url,
                                       data=dict(grant_type='password',
                                                 username='somebody',
                                                 scope='',
                                                 password='p@s$w0rd',
                                                 login_hint='%7B%22origin%22%3A%22uaa%22%7D'),
                                       headers=dict(Accept='application/json', Authorization='Basic Y2Y6'),
                                       proxies=dict(http='', https=''),
                                       verify=True)



