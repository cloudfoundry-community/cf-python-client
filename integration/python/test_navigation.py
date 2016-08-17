import logging
import unittest

from config_test import build_client_from_configuration

_logger = logging.getLogger(__name__)


class TestNavigation(unittest.TestCase):
    def test_all(self):
        client = build_client_from_configuration()
        for organization in client.organizations:
            if organization['metadata']['guid'] == client.org_guid:
                for space in organization.spaces():
                    if space['metadata']['guid'] == client.space_guid:
                        organization_reloaded = space.organization()
                        self.assertEqual(organization['metadata']['guid'], organization_reloaded['metadata']['guid'])
                        for application in space.apps():
                            if application['metadata']['guid'] == client.app_guid:
                                space_reloaded = application.space()
                                self.assertEqual(space['metadata']['guid'], space_reloaded['metadata']['guid'])
                                application.start()
                                application.stats()
                                application.instances()
                                application.summary()
                                for _ in application.routes():
                                    break
                                for _ in application.service_bindings():
                                    break
                                for _ in application.events():
                                    break
                                application.stop()
                        for service_instance in space.service_instances():
                            space_reloaded = service_instance.space()
                            self.assertEqual(space['metadata']['guid'], space_reloaded['metadata']['guid'])
                            for service_binding in service_instance.service_bindings():
                                service_instance_reloaded = service_binding.service_instance()
                                self.assertEqual(service_instance['metadata']['guid'],
                                                 service_instance_reloaded['metadata']['guid'])
                                service_binding.app()
                                break
                            for route in service_instance.routes():
                                service_instance_reloaded = route.service_instance()
                                self.assertEqual(service_instance['metadata']['guid'],
                                                 service_instance_reloaded['metadata']['guid'])
                                for _ in route.apps():
                                    break
                                space_reloaded = route.space()
                                self.assertEqual(space['metadata']['guid'], space_reloaded['metadata']['guid'])
                                break
                            service_plan = service_instance.service_plan()
                            for _ in service_plan.service_instances():
                                break
                            service = service_plan.service()
                            for _ in service.service_plans():
                                break
                            break
