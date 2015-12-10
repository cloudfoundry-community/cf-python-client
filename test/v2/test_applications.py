from config_test import build_client_from_configuration
from cloudfoundry_client import InvalidStatusCode
import unittest
import logging
import httplib
import json

_logger = logging.getLogger(__name__)


class TestApplications(unittest.TestCase):
    def test_list(self):
        cpt = 0
        client = build_client_from_configuration()
        for application in client.application.list(space_guid=client.space_guid):
            _logger.debug('- %s' % application['entity']['name'])
            if cpt == 0:
                self.assertIsNotNone(client.application.get_first(space_guid=client.space_guid,
                                                                  name=application['entity']['name']))
                self.assertIsNotNone(client.application.get(application['metadata']['guid']))
                try:
                    client.application.get('%s-0' % application['metadata']['guid'])
                    self.fail('Should not have been found')
                except InvalidStatusCode, e:
                    self.assertEquals(e.status_code, httplib.NOT_FOUND)
                instances = client.application.get_instances(application['metadata']['guid'])
                self.assertIsNotNone(instances)
                self.assertEquals(len(instances), application['entity']['instances'])
                _logger.debug('instances = %s', json.dumps(instances))
                stats = client.application.get_stats(application['metadata']['guid'])
                self.assertIsNotNone(stats)
                self.assertEquals(len(stats), application['entity']['instances'])
                self.assertEquals(len(stats), application['entity']['instances'])
                _logger.debug('stats = %s', json.dumps(stats))
                env = client.application.get_env(application['metadata']['guid'])
                self.assertIsNotNone(env)
                self.assertIsNotNone(env.get('application_env_json', None))
                self.assertIsNotNone(env['application_env_json'].get('VCAP_APPLICATION', None))
                self.assertGreater(len(env['application_env_json']['VCAP_APPLICATION'].get('application_uris', [])), 0)
                _logger.debug('env = %s', json.dumps(env))
            cpt += 1

        _logger.debug('test applications list - %d found', cpt)

    def test_start(self):
        client = build_client_from_configuration()
        _logger.debug('start - %s', client.application.start(client.app_guid, False))

    def test_stop(self):
        client = build_client_from_configuration()
        _logger.debug('stop - %s', client.application.stop(client.app_guid, False))
