import mock

from cloudfoundry_client.client import CloudFoundryClient
from cloudfoundry_client.loggregator.loggregator import LoggregatorManager
from cloudfoundry_client.v2.apps import AppManager
from cloudfoundry_client.v2.buildpacks import BuildpackManager
from cloudfoundry_client.v2.organizations import OrganizationManager
from cloudfoundry_client.v2.routes import RouteManager
from cloudfoundry_client.v2.service_bindings import ServiceBindingManager
from cloudfoundry_client.v2.service_brokers import ServiceBrokerManager
from cloudfoundry_client.v2.service_instances import ServiceInstanceManager
from cloudfoundry_client.v2.service_plans import ServicePlanManager
from cloudfoundry_client.v2.services import ServiceManager
from cloudfoundry_client.v2.spaces import SpaceManager
from fake_requests import TARGET_ENDPOINT


class AbstractTestCase(object):
    def build_client(self):
        self.client = mock.MagicMock(spec=CloudFoundryClient)
        self.client.organizations = OrganizationManager(TARGET_ENDPOINT, self.client)
        self.client.spaces = SpaceManager(TARGET_ENDPOINT, self.client)
        self.client.services = ServiceManager(TARGET_ENDPOINT, self.client)
        self.client.service_plans = ServicePlanManager(TARGET_ENDPOINT, self.client)
        self.client.service_instances = ServiceInstanceManager(TARGET_ENDPOINT, self.client)
        self.client.service_bindings = ServiceBindingManager(TARGET_ENDPOINT, self.client)
        self.client.service_brokers = ServiceBrokerManager(TARGET_ENDPOINT, self.client)
        self.client.apps = AppManager(TARGET_ENDPOINT, self.client)
        self.client.buildpacks = BuildpackManager(TARGET_ENDPOINT, self.client)
        self.client.routes = RouteManager(TARGET_ENDPOINT, self.client)
        self.client.loggregator = LoggregatorManager(TARGET_ENDPOINT, self.client)
