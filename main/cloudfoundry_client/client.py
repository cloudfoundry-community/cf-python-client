import logging

import requests
from oauth2_client.credentials_manager import CredentialManager, ServiceInformation

from cloudfoundry_client.doppler.client import DopplerClient
from cloudfoundry_client.errors import InvalidStatusCode
from cloudfoundry_client.imported import UNAUTHORIZED
from cloudfoundry_client.v2.jobs import JobManager
from cloudfoundry_client.v2.resources import ResourceManager
from cloudfoundry_client.v2.apps import AppManager as AppManagerV2
from cloudfoundry_client.v2.buildpacks import BuildpackManager
from cloudfoundry_client.v2.entities import EntityManager as EntityManagerV2
from cloudfoundry_client.v2.routes import RouteManager
from cloudfoundry_client.v2.service_bindings import ServiceBindingManager
from cloudfoundry_client.v2.service_brokers import ServiceBrokerManager
from cloudfoundry_client.v2.service_instances import ServiceInstanceManager
from cloudfoundry_client.v2.service_keys import ServiceKeyManager
from cloudfoundry_client.v2.service_plans import ServicePlanManager
from cloudfoundry_client.v3.apps import AppManager as AppManagerV3
from cloudfoundry_client.v3.entities import EntityManager as EntityManagerV3
from cloudfoundry_client.v3.tasks import TaskManager

_logger = logging.getLogger(__name__)


class Info:
    def __init__(self, api_version, authorization_endpoint, api_endpoint, doppler_endpoint):
        self.api_version = api_version
        self.authorization_endpoint = authorization_endpoint
        self.api_endpoint = api_endpoint
        self.doppler_endpoint = doppler_endpoint


class V2(object):
    def __init__(self, target_endpoint, credential_manager):
        self.apps = AppManagerV2(target_endpoint, credential_manager)
        self.buildpacks = BuildpackManager(target_endpoint, credential_manager)
        self.jobs = JobManager(target_endpoint, credential_manager)
        self.service_bindings = ServiceBindingManager(target_endpoint, credential_manager)
        self.service_brokers = ServiceBrokerManager(target_endpoint, credential_manager)
        self.service_instances = ServiceInstanceManager(target_endpoint, credential_manager)
        self.service_keys = ServiceKeyManager(target_endpoint, credential_manager)
        self.service_plans = ServicePlanManager(target_endpoint, credential_manager)
        # Default implementations
        self.organizations = EntityManagerV2(target_endpoint, credential_manager, '/v2/organizations')
        self.private_domains = EntityManagerV2(target_endpoint, credential_manager, '/v2/private_domains')
        self.routes = RouteManager(target_endpoint, credential_manager)
        self.services = EntityManagerV2(target_endpoint, credential_manager, '/v2/services')
        self.shared_domains = EntityManagerV2(target_endpoint, credential_manager, '/v2/shared_domains')
        self.spaces = EntityManagerV2(target_endpoint, credential_manager, '/v2/spaces')
        self.stacks = EntityManagerV2(target_endpoint, credential_manager, '/v2/stacks')
        self.user_provided_service_instances = EntityManagerV2(target_endpoint, credential_manager,
                                                               '/v2/user_provided_service_instances')
        # Resources implementation used by push operation
        self.resources = ResourceManager(target_endpoint, credential_manager)


class V3(object):
    def __init__(self, target_endpoint, credential_manager):
        self.apps = AppManagerV3(target_endpoint, credential_manager)
        self.spaces = EntityManagerV3(target_endpoint, credential_manager, '/v3/spaces')
        self.organizations = EntityManagerV3(target_endpoint, credential_manager, '/v3/organizations')
        self.tasks = TaskManager(target_endpoint, credential_manager)


class CloudFoundryClient(CredentialManager):
    def __init__(self, target_endpoint, client_id='cf', client_secret='', **kwargs):
        """"
        :param target_endpoint :the target endpoint
        :param client_id: the client_id
        :param client_secret: the client secret
        :param proxy: a dict object with entries http and https
        :param verify: parameter directly passed to underlying requests library.
            (optional) Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. Defaults to ``True``.
        :param token_format: string Can be set to opaque to retrieve an opaque and revocable token.
            See UAA API specifications
        :param login_hint: string. Indicates the identity provider to be used.
            The passed string has to be a URL-Encoded JSON Object, containing the field origin with value as origin_key
            of an identity provider. Note that this identity provider must support the grant type password.
            See UAA API specifications
        """
        proxy = kwargs.get('proxy', dict(http='', https=''))
        verify = kwargs.get('verify', True)
        self.token_format = kwargs.get('token_format')
        self.login_hint = kwargs.get('login_hint')
        info = self._get_info(target_endpoint, proxy, verify=verify)
        if not info.api_version.startswith('2.'):
            raise AssertionError('Only version 2 is supported for now. Found %s' % info.api_version)
        service_information = ServiceInformation(None, '%s/oauth/token' % info.authorization_endpoint,
                                                 client_id, client_secret, [], verify)
        super(CloudFoundryClient, self).__init__(service_information, proxies=proxy)
        self.v2 = V2(target_endpoint, self)
        self.v3 = V3(target_endpoint, self)
        self._doppler = DopplerClient(info.doppler_endpoint,
                                      self.proxies[
                                          'http' if info.doppler_endpoint.startswith('ws://') else 'https'],
                                      self.service_information.verify,
                                      self) if info.doppler_endpoint is not None else None
        self.info = info

    @property
    def doppler(self):
        if self._doppler is None:
            raise NotImplementedError('No droppler endpoint for this instance')
        else:

            return self._doppler

    @staticmethod
    def _get_info(target_endpoint, proxy=None, verify=True):
        info_response = CloudFoundryClient._check_response(requests.get('%s/v2/info' % target_endpoint,
                                                                        proxies=proxy if proxy is not None else dict(
                                                                            http='', https=''),
                                                                        verify=verify))
        info = info_response.json()
        return Info(info['api_version'],
                    info['authorization_endpoint'],
                    target_endpoint,
                    info.get('doppler_logging_endpoint'))

    @staticmethod
    def _is_token_expired(response):
        if response.status_code == UNAUTHORIZED:
            try:
                json_data = response.json()
                result = json_data.get('code', 0) == 1000 and json_data.get('error_code', '') == 'CF-InvalidAuthToken'
                _logger.info('_is_token_expired - %s' % str(result))
                return result
            except Exception as _:
                return False
        else:
            return False

    @staticmethod
    def _token_request_headers(_):
        return dict(Accept='application/json')

    def _grant_password_request(self, login, password):
        request = super(CloudFoundryClient, self)._grant_password_request(login, password)
        if self.token_format is not None:
            request['token_format'] = self.token_format
        if self.login_hint is not None:
            request['login_hint'] = self.login_hint
        return request

    def _grant_refresh_token_request(self, refresh_token):
        request = super(CloudFoundryClient, self)._grant_refresh_token_request(refresh_token)
        if self.token_format is not None:
            request['token_format'] = self.token_format
        return request

    def get(self, url, params=None, **kwargs):
        response = super(CloudFoundryClient, self).get(url, params, **kwargs)
        return CloudFoundryClient._check_response(response)

    def post(self, url, data=None, json=None, **kwargs):
        response = super(CloudFoundryClient, self).post(url, data, json, **kwargs)
        return CloudFoundryClient._check_response(response)

    def put(self, url, data=None, json=None, **kwargs):
        response = super(CloudFoundryClient, self).put(url, data, json, **kwargs)
        return CloudFoundryClient._check_response(response)

    def patch(self, url, data=None, json=None, **kwargs):
        response = super(CloudFoundryClient, self).patch(url, data, json, **kwargs)
        return CloudFoundryClient._check_response(response)

    def delete(self, url, **kwargs):
        response = super(CloudFoundryClient, self).delete(url, **kwargs)
        return CloudFoundryClient._check_response(response)

    @staticmethod
    def _check_response(response):
        if int(response.status_code / 100) == 2:
            return response
        else:
            try:
                body = response.json()
            except Exception as _:
                body = response.text
            raise InvalidStatusCode(response.status_code, body)
