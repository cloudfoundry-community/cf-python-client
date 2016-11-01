import logging
import unittest

from config_test import build_client_from_configuration

_logger = logging.getLogger(__name__)


class TestServiceBrokers(unittest.TestCase):
    def test_list(self):
        cpt = 0
        client = build_client_from_configuration()
        for broker in client.service_brokers.list():
            if cpt == 0:
                self.assertIsNotNone(
                    client.service_brokers.get_first(space_guid=broker['entity']['space_guid']))
                self.assertIsNotNone(
                    client.service_brokers.get(broker['metadata']['guid']))
            cpt += 1
            _logger.debug(broker)
        _logger.debug('test broker list - %d found', cpt)
