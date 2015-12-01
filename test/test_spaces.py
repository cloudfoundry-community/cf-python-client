from config_test import build_client_from_configuration
import unittest
import logging

_logger = logging.getLogger(__name__)


class TestSpaces(unittest.TestCase):
    def test_list(self):
        cpt = 0
        client = build_client_from_configuration()
        for _ in client.space.list(client.org_guid):
            cpt += 1
        _logger.debug('test spaces list - %d found', cpt)


if __name__ == '__main__':
    unittest.main()