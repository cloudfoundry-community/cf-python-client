import base64
import httplib
import logging
from cloudfoundry_client.calls import OutputFormat

_logger = logging.getLogger(__name__)

from cloudfoundry_client.calls import caller, InvalidStatusCode


class InvalidCredentials(Exception):
    pass


class CredentialsManager(object):
    def __init__(self, authorization_endpoint, client_id, client_secret):
        self.authorization_endpoint = authorization_endpoint
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

    def access_token(self):
        return self.credentials['access_token'] if self.credentials is not None else None

    def refresh_token(self):
        return self.credentials['refresh_token'] if self.credentials is not None else None

    def get(self, url, output_format=OutputFormat.JSON):
        return self._bearer_request(caller.get, url, None, output_format)

    def post(self, url, data, output_format=OutputFormat.JSON):
        return self._bearer_request(caller.post, url, data, output_format)

    def put(self, url, data, output_format=OutputFormat.JSON):
        return self._bearer_request(caller.put, url, data, output_format)

    def delete(self, url, output_format=OutputFormat.TEXT):
        return self._bearer_request(caller.delete, url, None, output_format)

    def _bearer_request(self, method, url, data_json, output_format):
        if self.credentials is None:
            raise InvalidCredentials()
        parameters = dict(headers=dict(
            Authorization='Bearer %s' %
                          self.credentials['access_token']),
                          output_format=output_format)
        if data_json is not None:
            parameters['json'] = data_json
        try:
            return method(url, **parameters)
        except InvalidStatusCode, s:
            if s.status_code == httplib.UNAUTHORIZED:
                _logger.debug('token expired. refreshing it')
                self._refresh_access_token()
                try:
                    _logger.debug('token refreshed')
                    parameters['headers']['Authorization'] = 'Bearer %s' % self.credentials['access_token']
                    return method(url, **parameters)
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
        self.credentials = caller.post('%s/oauth/token' % self.authorization_endpoint,
                                       data=data,
                                       headers=dict(Authorization=
                                                    'Basic %s' % base64.b64encode(
                                                        '%s:%s' % (self.client_id, self.client_secret))
                                                    ),
                                       output_format=OutputFormat.JSON
                                       )

