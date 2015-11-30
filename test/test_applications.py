from config_test import build_client_from_configuration
import unittest
import logging

_logger = logging.getLogger(__name__)


class TestApplications(unittest.TestCase):
    def test_list(self):
        cpt = 0
        client = build_client_from_configuration()
        for _ in client.application.list(client.space_guid):
            cpt += 1
        _logger.debug('test applications list - %d found', cpt)

    def test_start(self):
        client = build_client_from_configuration()
        client.application.start(client.app_guid, False)
        _logger.debug('test application start - started')

    def test_stop(self):
        client = build_client_from_configuration()
        client.application.stop(client.app_guid, False)
        _logger.debug('test application stop - stopped')


if __name__ == '__main__':
    unittest.main()