from config_test import build_client_from_configuration
import unittest
import logging
import json

_logger = logging.getLogger(__name__)


class TestOrganizations(unittest.TestCase):
    def test_list(self):
        cpt = 0
        client = build_client_from_configuration()
        for organization in client.organization.list():
            if cpt == 0:
                organization = client.organization.get(organization['metadata']['guid'])
                self.assertIsNotNone(organization)
                organization = client.organization.get_first(name=organization['entity']['name'])
                self.assertIsNotNone(organization)
                _logger.debug(json.dumps(organization))
            cpt += 1
        _logger.debug('test organization list - %d found', cpt)
