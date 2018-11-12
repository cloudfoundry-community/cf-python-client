import logging
import unittest

from config_test import build_client_from_configuration

_logger = logging.getLogger(__name__)


class TestSpaces(unittest.TestCase):
    def test_list(self):
        cpt = 0
        client = build_client_from_configuration()
        for space in client.v2.spaces.list(organization_guid=client.org_guid):
            _logger.debug(' - %s' % space['entity']['name'])
            if cpt == 0:
                space = client.v2.spaces.get(space['metadata']['guid'])
                self.assertIsNotNone(space)
                space = client.v2.spaces.get_first(organization_guid=client.org_guid, name=space['entity']['name'])
                self.assertIsNotNone(space)
            cpt += 1
        _logger.debug('test spaces list - %d found', cpt)
