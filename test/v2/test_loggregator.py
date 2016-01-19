import unittest
import logging

from config_test import build_client_from_configuration


_logger = logging.getLogger(__name__)


class TestLoggregator(unittest.TestCase):
    def test_log_recent(self):
        client = build_client_from_configuration()
        _logger.debug('test_log_recent:\n%s' % client.loggregator.get_recent(client.log_app_guid))
