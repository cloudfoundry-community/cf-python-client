from config_test import build_client_from_configuration
import unittest
import logging

_logger = logging.getLogger(__name__)


class TestServices(unittest.TestCase):
    def test_list_services(self):
        cpt = 0
        client = build_client_from_configuration()
        for service in client.v2.services.list():
            _logger.debug("- %s" % service["entity"]["label"])
            if cpt == 0:
                service = client.v2.services.get_first(label=service["entity"]["label"])
                self.assertIsNotNone(service)
            cpt += 1

        _logger.debug("test service list - %d found", cpt)
