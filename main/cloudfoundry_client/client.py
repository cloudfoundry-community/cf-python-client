from cloudfoundry_client.imported import OK, UNAUTHORIZED
import logging

import requests
from oauth2_client.credentials_manager import CredentialManager, ServiceInformation

from cloudfoundry_client.entities import InvalidStatusCode, EntityManager
from cloudfoundry_client.v2.apps import AppManager
from cloudfoundry_client.v2.buildpacks import BuildpackManager
from cloudfoundry_client.v2.service_bindings import ServiceBindingManager
from cloudfoundry_client.v2.service_brokers import ServiceBrokerManager
from cloudfoundry_client.v2.service_instances import ServiceInstanceManager
from cloudfoundry_client.v2.service_keys import ServiceKeyManager
from cloudfoundry_client.v2.service_plans import ServicePlanManager

_logger = logging.getLogger(__name__)


class CloudFoundryClient(CredentialManager):
    def __init__(self, target_endpoint, client_id='cf', client_secret='', proxy=None, skip_verification=False):
        info = self.get_info(target_endpoint, proxy, skip_verification)
        if not info['api_version'].startswith('2.'):
            raise AssertionError('Only version 2 is supported for now. Found %s' % info['api_version'])

        service_informations = ServiceInformation(None, '%s/oauth/token' % info['authorization_endpoint'],
                                                  client_id, client_secret, [], skip_verification)
        super(CloudFoundryClient, self).__init__(service_informations, proxy)
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
        self._loggregator_endpoint = info.get('logging_endpoint', None)
        self._loggregator = None

    @property
    def loggregator(self):
        if self._loggregator is None:
            if self._loggregator_endpoint is None:
                raise NotImplementedError('No loggregator endpoint for this instance')
            else:
                from cloudfoundry_client.loggregator.loggregator import LoggregatorManager
                self._loggregator = LoggregatorManager(self._loggregator_endpoint, self)
        return self._loggregator

    @staticmethod
    def get_info(target_endpoint, proxy=None, skip_verification=False):
        # to get loggregator url
        info_response = requests.get('%s/v2/info' % target_endpoint,
                                     proxies=proxy if proxy is not None else dict(http='', https=''),
                                     verify=not skip_verification)
        if info_response.status_code != OK:
            raise InvalidStatusCode(info_response.status_code, info_response.text)
        info = info_response.json()
        return info

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
