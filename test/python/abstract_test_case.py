import mock

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
from fake_requests import TARGET_ENDPOINT


class AbstractTestCase(object):
    def build_client(self):
        self.client = mock.MagicMock()
        self.client.organization = OrganizationManager(TARGET_ENDPOINT, self.client)
        self.client.space = SpaceManager(TARGET_ENDPOINT, self.client)
        self.client.service = ServiceManager(TARGET_ENDPOINT, self.client)
        self.client.service_plan = ServicePlanManager(TARGET_ENDPOINT, self.client)
        self.client.service_instance = ServiceInstanceManager(TARGET_ENDPOINT, self.client)
        self.client.service_binding = ServiceBindingManager(TARGET_ENDPOINT, self.client)
        self.client.service_broker = ServiceBrokerManager(TARGET_ENDPOINT, self.client)
        self.client.application = ApplicationManager(TARGET_ENDPOINT, self.client)
        self.client.buildpack = BuildpackManager(TARGET_ENDPOINT, self.client)
        self.client.route = RouteManager(TARGET_ENDPOINT, self.client)
        self.client.loggregator = LoggregatorManager(TARGET_ENDPOINT, self.client)
