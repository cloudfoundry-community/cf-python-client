import base64
import httplib
import logging


_logger = logging.getLogger(__name__)

from cloudfoundry_client.calls import caller, InvalidStatusCode


class InvalidCredentials(Exception):
    pass


class CredentialsManager(object):
    def __init__(self, info, client_id, client_secret):
        self.info = info
        self.credentials = None
        self.client_id = client_id
        self.client_secret = client_secret

    def init_with_credentials(self, login, password):
        _logger.debug('init_with_credentials - %s', login)
        self._credentials_request(dict(grant_type='password', username=login, password=password))

    def init_with_tokens(self, access_token, refresh_token):
        self.credentials = dict(access_token=access_token, refresh_token=refresh_token)

    def init_with_refresh(self, refresh_token):
        self._credentials_request(dict(grant_type='refresh_token', scope='', refresh_token=refresh_token))

    def init_with_refresh(self, refresh_token):
        self._credentials_request(dict(grant_type='refresh_token', scope='', refresh_token=refresh_token))

    def access_token(self):
        return self.credentials['access_token'] if self.credentials is not None else None

    def refresh_token(self):
        return self.credentials['refresh_token'] if self.credentials is not None else None

    def get(self, url, **kwargs):
        return self._bearer_request(caller.get, url, True, **kwargs)

    def post(self, url, **kwargs):
        return self._bearer_request(caller.post, url, True, **kwargs)

    def put(self, url, **kwargs):
        return self._bearer_request(caller.put, url, True, **kwargs)

    def delete(self, url, **kwargs):
        return self._bearer_request(caller.delete, url, False, **kwargs)

    def _bearer_request(self, method, url, json_output, **kwargs):
        if self.credentials is None:
            raise InvalidCredentials()
        try:
            response = method(url,
                              headers=dict(
                                  Authorization='Bearer %s' %
                                                self.credentials['access_token']),
                              **kwargs)
            if json_output:
                return response.json()
            else:
                return response.text

        except InvalidStatusCode, s:
            if s.status_code == httplib.UNAUTHORIZED:
                _logger.debug('token expired. refreshing it')
                self._refresh_access_token()
                try:
                    _logger.debug('token refreshed')
                    response = method(url,
                                      headers=dict(
                                          Authorization='Bearer %s' %
                                                        self.credentials['access_token']),
                                      **kwargs)
                    if json_output:
                        return response.json()
                    else:
                        return response.text
                except InvalidStatusCode, s:
                    if s.status_code == httplib.UNAUTHORIZED:
                        _logger.debug('token still invalid. erasing it')
                        self.credentials = None
                    raise
            else:
                raise

    def _refresh_access_token(self):
        try:
            self.init_with_refresh(self.credentials['refresh_token'])
        except InvalidStatusCode, s:
            self.credentials = None
            raise s

    def _credentials_request(self, data):
        response = caller.post('%s/oauth/token' % self.info['authorization_endpoint'],
                               data=data,
                               headers=dict(Authorization=
                                            'Basic %s' % base64.b64encode(
                                                '%s:%s' % (self.client_id, self.client_secret))
                                            )
                               )
        self.credentials = response.json()

