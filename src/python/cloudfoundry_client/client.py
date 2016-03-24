import logging

from cloudfoundry_client.calls import caller, OutputFormat
from cloudfoundry_client.credentials import CredentialsManager
from cloudfoundry_client.v2.organizations import OrganizationManager
from cloudfoundry_client.v2.spaces import SpaceManager
from cloudfoundry_client.v2.services import ServiceManager
from cloudfoundry_client.v2.service_plans import ServicePlanManager
from cloudfoundry_client.v2.service_instances import ServiceInstanceManager
from cloudfoundry_client.v2.service_bindings import ServiceBindingManager
from cloudfoundry_client.v2.service_brokers import ServiceBrokerManager
from cloudfoundry_client.v2.applications import ApplicationsManager
from cloudfoundry_client.loggregator.loggregator import LoggregatorManager

_logger = logging.getLogger(__name__)


class InvalidStatusCode(Exception):
    def __init__(self, status_code):
        self.status_code = status_code


class CloudFoundryClient(object):
    proxy = None

    def __init__(self, target_endpoint, client_id='cf', client_secret='', proxy=None, skip_verification=False):
        caller.proxy(proxy)
        caller.skip_verifications(skip_verification)
        # to get loggregator url
        info = caller.get('%s/v2/info' % target_endpoint, output_format=OutputFormat.JSON)
        if not info['api_version'].startswith('2.'):
            raise AssertionError('Only version 2 is supported for now. Found %s' % info['api_version'])

        self.credentials_manager = CredentialsManager(info['authorization_endpoint'], client_id, client_secret)
        self.organization = OrganizationManager(target_endpoint, self.credentials_manager)
        self.space = SpaceManager(target_endpoint, self.credentials_manager)
        self.service = ServiceManager(target_endpoint, self.credentials_manager)
        self.service_plan = ServicePlanManager(target_endpoint, self.credentials_manager)
        self.service_instance = ServiceInstanceManager(target_endpoint, self.credentials_manager)
        self.service_binding = ServiceBindingManager(target_endpoint, self.credentials_manager)
        self.service_broker = ServiceBrokerManager(target_endpoint, self.credentials_manager)
        self.application = ApplicationsManager(target_endpoint, self.credentials_manager)
        self.loggregator = LoggregatorManager(info['logging_endpoint'], self.credentials_manager)

    def init_with_credentials(self, login, password):
        self.credentials_manager.init_with_credentials(login, password)

    def init_with_refresh(self, refresh_token):
        self.credentials_manager.init_with_refresh(refresh_token)



