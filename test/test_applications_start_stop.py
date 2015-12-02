from config_test import build_client_from_configuration
from cloudfoundry_client import InvalidStatusCode
import unittest
import logging
import json
import httplib

_logger = logging.getLogger(__name__)


class TestApplicationsStartStop(unittest.TestCase):
    def test_start_stop(self):
        client = build_client_from_configuration()
        self._print_instances(client)
        self._print_stats(client)
        _logger.debug('test_start_stop - starting')
        result = client.application.start(client.app_guid)
        _logger.debug('test_start_stop - result - %s', json.dumps(result))
        self._print_instances(client)
        self._print_stats(client)
        _logger.debug('test_start_stop - stopping')
        result = client.application.stop(client.app_guid)
        _logger.debug('test_start_stop - result - %s', json.dumps(result))
        self._print_instances(client)
        self._print_stats(client)

    def _print_instances(self, client):
        try:
            instances = client.application.get_instances(client.app_guid)
            _logger.debug('test_start_stop - instances - %s', json.dumps(instances))
        except InvalidStatusCode, ex:
            if ex.status_code == httplib.BAD_REQUEST and isinstance(ex.body, dict) \
                    and ex.body.get('error_code', '') == "CF-InstancesError":
                _logger.debug('application stopped')
            else:
                raise

    def _print_stats(self, client):
        try:
            stats = client.application.get_stats(client.app_guid)
            _logger.debug('test_start_stop - stats - %s', json.dumps(stats))
        except InvalidStatusCode, ex:
            if ex.status_code == httplib.BAD_REQUEST and isinstance(ex.body, dict) \
                    and ex.body.get('error_code', '') == "CF-AppStoppedStatsError":
                _logger.debug('application stopped')
            else:
                raise



