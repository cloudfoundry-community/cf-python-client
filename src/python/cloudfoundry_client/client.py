import logging

import requests
import httplib
from oauth2_client.credentials_manager import CredentialManager, ServiceInformation
from cloudfoundry_client.entities import InvalidStatusCode
from cloudfoundry_client.loggregator.loggregator import LoggregatorManager
from cloudfoundry_client.v2.applications import ApplicationManager
from cloudfoundry_client.v2.buildpacks import BuildpackManager
from cloudfoundry_client.v2.organizations import OrganizationManager
from cloudfoundry_client.v2.routes import RouteManager
from cloudfoundry_client.v2.service_bindings import ServiceBindingManager
from cloudfoundry_client.v2.service_brokers import ServiceBrokerManager
from cloudfoundry_client.v2.service_instances import ServiceInstanceManager
from cloudfoundry_client.v2.service_plans import ServicePlanManager
from cloudfoundry_client.v2.services import ServiceManager
from cloudfoundry_client.v2.spaces import SpaceManager

_logger = logging.getLogger(__name__)


class CloudFoundryClient(object):
    proxy = None

    def __init__(self, target_endpoint, client_id='cf', client_secret='', proxy=None, skip_verification=False):
        info = self.get_info(target_endpoint, proxy, skip_verification)
        if not info['api_version'].startswith('2.'):
            raise AssertionError('Only version 2 is supported for now. Found %s' % info['api_version'])

        service_informations = ServiceInformation(None, '%s/oauth/token' % info['authorization_endpoint'],
                                                  client_id, client_secret, [], skip_verification)
        self.credentials_manager = CredentialManager(service_informations, proxy)
        self.organization = OrganizationManager(target_endpoint, self.credentials_manager)
        self.space = SpaceManager(target_endpoint, self.credentials_manager)
        self.service = ServiceManager(target_endpoint, self.credentials_manager)
        self.service_plan = ServicePlanManager(target_endpoint, self.credentials_manager)
        self.service_instance = ServiceInstanceManager(target_endpoint, self.credentials_manager)
        self.service_binding = ServiceBindingManager(target_endpoint, self.credentials_manager)
        self.service_broker = ServiceBrokerManager(target_endpoint, self.credentials_manager)
        self.application = ApplicationManager(target_endpoint, self.credentials_manager)
        self.buidlpack = BuildpackManager(target_endpoint, self.credentials_manager)
        self.route = RouteManager(target_endpoint, self.credentials_manager)
        self.loggregator = LoggregatorManager(info['logging_endpoint'], self.credentials_manager)

    def init_with_credentials(self, login, password):
        self.credentials_manager.init_with_user_credentials(login, password)

    def init_with_refresh(self, refresh_token):
        self.credentials_manager.init_with_token(refresh_token)

    @staticmethod
    def get_info(target_endpoint, proxy=None, skip_verification=False):
        # to get loggregator url
        info_response = requests.get('%s/v2/info' % target_endpoint,
                                     proxies=proxy if proxy is not None else dict(http='', https=''),
                                     verify=not skip_verification)
        if info_response.status_code != httplib.OK:
            print info_response.status_code
            raise InvalidStatusCode(info_response.status_code, info_response.text)
        info = info_response.json()
        return info


