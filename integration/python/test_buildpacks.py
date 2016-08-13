import unittest
import logging
import json

from config_test import build_client_from_configuration


_logger = logging.getLogger(__name__)


class TestBuildpacks(unittest.TestCase):
    def test_list(self):
        client = build_client_from_configuration()
        for buildpack in client.buidlpack.list():
            _logger.debug(' %s' % json.dumps(buildpack))
