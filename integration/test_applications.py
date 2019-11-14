import json
import logging
import unittest
from http import HTTPStatus

from config_test import build_client_from_configuration

from cloudfoundry_client.errors import InvalidStatusCode

_logger = logging.getLogger(__name__)


class TestApps(unittest.TestCase):
    def test_list(self):
        cpt = 0
        client = build_client_from_configuration()
        for application in client.v2.apps.list(space_guid=client.space_guid):
            _logger.debug('- %s' % application['entity']['name'])
            if cpt == 0:
                _logger.debug('- %s' % application['metadata']['guid'])
                self.assertIsNotNone(client.v2.apps.get_first(space_guid=client.space_guid,
                                                                  name=application['entity']['name']))
                self.assertIsNotNone(client.v2.apps.get(application['metadata']['guid']))
                try:
                    client.v2.apps.get('%s-0' % application['metadata']['guid'])
                    self.fail('Should not have been found')
                except InvalidStatusCode as e:
                    self.assertEquals(e.status_code, HTTPStatus.NOT_FOUND)
                try:
                    instances = client.v2.apps.get_instances(application['metadata']['guid'])
                    self.assertIsNotNone(instances)
                    self.assertEquals(len(instances), application['entity']['instances'])
                    _logger.debug('instances = %s', json.dumps(instances))
                except InvalidStatusCode as e:
                    #instance is stopped
                    self.assertEquals(e.status_code, HTTPStatus.BAD_REQUEST)
                    self.assertIsInstance(e.body, dict)
                    self.assertEqual(e.body.get('error_code'), 'CF-InstancesError')
                try:
                    stats = client.v2.apps.get_stats(application['metadata']['guid'])
                    self.assertIsNotNone(stats)
                    self.assertEquals(len(stats), application['entity']['instances'])
                    self.assertEquals(len(stats), application['entity']['instances'])
                    _logger.debug('stats = %s', json.dumps(stats))
                except InvalidStatusCode as e:
                    # instance is stopped
                    self.assertEquals(e.status_code, HTTPStatus.BAD_REQUEST)
                    self.assertIsInstance(e.body, dict)
                    self.assertEqual(e.body.get('error_code'), 'CF-AppStoppedStatsError')
                env = client.v2.apps.get_env(application['metadata']['guid'])
                self.assertIsNotNone(env)
                self.assertIsNotNone(env.get('application_env_json', None))
                self.assertIsNotNone(env['application_env_json'].get('VCAP_APPLICATION', None))
                self.assertGreater(len(env['application_env_json']['VCAP_APPLICATION'].get('application_uris', [])), 0)
                _logger.debug('env = %s', json.dumps(env))
            cpt += 1

        _logger.debug('test applications list - %d found', cpt)

    def test_start(self):
        client = build_client_from_configuration()

        _logger.debug('start - %s', client.v2.apps.start(client.app_guid, async=False))

    def test_stop(self):
        client = build_client_from_configuration()
        _logger.debug('stop - %s', client.v2.apps.stop(client.app_guid, async=False))

