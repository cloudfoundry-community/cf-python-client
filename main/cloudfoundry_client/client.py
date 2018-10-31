import logging

import requests
from oauth2_client.credentials_manager import CredentialManager, ServiceInformation

from cloudfoundry_client.doppler.client import DopplerClient
from cloudfoundry_client.entities import EntityManager
from cloudfoundry_client.errors import InvalidStatusCode
from cloudfoundry_client.imported import UNAUTHORIZED
from cloudfoundry_client.v2.apps import AppManager
from cloudfoundry_client.v2.buildpacks import BuildpackManager
from cloudfoundry_client.v2.service_bindings import ServiceBindingManager
from cloudfoundry_client.v2.service_brokers import ServiceBrokerManager
from cloudfoundry_client.v2.service_instances import ServiceInstanceManager
from cloudfoundry_client.v2.service_keys import ServiceKeyManager
from cloudfoundry_client.v2.service_plans import ServicePlanManager

_logger = logging.getLogger(__name__)


class Info:
    def __init__(self, api_version, authorization_endpoint, doppler_endpoint):
        self.api_version = api_version
        self.authorization_endpoint = authorization_endpoint
        self.doppler_endpoint = doppler_endpoint


class CloudFoundryClient(CredentialManager):
    def __init__(self, target_endpoint, client_id='cf', client_secret='', proxy=None, skip_verification=False):
        self.info = self._get_info(target_endpoint, proxy, skip_verification)
        if not self.info.api_version.startswith('2.'):
            raise AssertionError('Only version 2 is supported for now. Found %s' % self.info.api_version)

        service_informations = ServiceInformation(None, '%s/oauth/token' % self.info.authorization_endpoint,
                                                  client_id, client_secret, [], skip_verification)
        super(CloudFoundryClient, self).__init__(service_informations, proxy)
        CredentialManager.__init__(self, service_informations, proxy)
        self.service_plans = ServicePlanManager(target_endpoint, self)
        self.service_instances = ServiceInstanceManager(target_endpoint, self)
        self.service_keys = ServiceKeyManager(target_endpoint, self)
        self.service_bindings = ServiceBindingManager(target_endpoint, self)
        self.service_brokers = ServiceBrokerManager(target_endpoint, self)
        self.apps = AppManager(target_endpoint, self)
        self.buildpacks = BuildpackManager(target_endpoint, self)
        # Default implementations
        self.organizations = EntityManager(target_endpoint, self, '/v2/organizations')
        self.spaces = EntityManager(target_endpoint, self, '/v2/spaces')
        self.services = EntityManager(target_endpoint, self, '/v2/services')
        self.routes = EntityManager(target_endpoint, self, '/v2/routes')
        self._doppler = DopplerClient(self.info.doppler_endpoint,
                                      self.proxies[
                                          'http' if self.info.doppler_endpoint.startswith('ws://') else 'https'],
                                      not self.service_information.skip_ssl_verifications,
                                      self) if self.info.doppler_endpoint is not None else None

    @property
    def doppler(self):
        if self._doppler is None:
            raise NotImplementedError('No droppler endpoint for this instance')
        else:

            return self._doppler

    @staticmethod
    def _get_info(target_endpoint, proxy=None, skip_verification=False):
        info_response = CloudFoundryClient._check_response(requests.get('%s/v2/info' % target_endpoint,
                                                                        proxies=proxy if proxy is not None else dict(
                                                                            http='', https=''),
                                                                        verify=not skip_verification))
        info = info_response.json()
        return Info(info['api_version'],
                    info['authorization_endpoint'],
                    info.get('doppler_logging_endpoint'))

    @staticmethod
    def _is_token_expired(response):
        if response.status_code == UNAUTHORIZED:
            try:
                json_data = response.json()
                result = json_data.get('code', 0) == 1000 and json_data.get('error_code', '') == 'CF-InvalidAuthToken'
                _logger.info('_is_token_expired - %s' % str(result))
                return result
            except:
                return False
        else:
            return False

    @staticmethod
    def _token_request_headers(_):
        return dict(Accept='application/json')

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
