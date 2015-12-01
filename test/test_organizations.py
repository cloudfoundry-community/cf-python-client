from config_test import build_client_from_configuration
import unittest
import logging

_logger = logging.getLogger(__name__)


class TestOrganizations(unittest.TestCase):
    def test_list(self):
        cpt = 0
        for _ in build_client_from_configuration().organization.list():
            cpt += 1
        _logger.debug('test organization list - %d found', cpt)
