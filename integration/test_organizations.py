from config_test import build_client_from_configuration
import unittest
import logging

_logger = logging.getLogger(__name__)


class TestOrganizations(unittest.TestCase):
    def test_list(self):
        cpt = 0
        client = build_client_from_configuration()
        for organization in client.v2.organizations.list():
            if cpt == 0:
                organization = client.v2.organizations.get(organization["metadata"]["guid"])
                self.assertIsNotNone(organization)
                organization = client.v2.organizations.get_first(name=organization["entity"]["name"])
                self.assertIsNotNone(organization)
                _logger.debug(organization.json())
            cpt += 1
        _logger.debug("test organization list - %d found", cpt)
