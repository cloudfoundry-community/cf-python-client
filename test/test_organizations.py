from config_test import build_client_from_configuration
import unittest
import logging

_logger = logging.getLogger(__name__)


class TestOrganizations(unittest.TestCase):
    def test_list(self):
        cpt = 0
        client = build_client_from_configuration()
        for organization in client.organization.list():
            if cpt == 0:
                client.organization.get_by_id(organization['metadata']['guid'])
            cpt += 1
        _logger.debug('test organization list - %d found', cpt)
