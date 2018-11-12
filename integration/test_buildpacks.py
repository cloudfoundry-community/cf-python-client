import logging
import unittest

from config_test import build_client_from_configuration

_logger = logging.getLogger(__name__)


class TestBuildpacks(unittest.TestCase):
    def test_list(self):
        client = build_client_from_configuration()
        for buildpack in client.v2.buildpacks.list():
            _logger.debug(' %s' % buildpack.json())
