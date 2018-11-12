import logging
import unittest

from config_test import build_client_from_configuration

_logger = logging.getLogger(__name__)


class TestServiceKeys(unittest.TestCase):
    def test_create_delete(self):
        client = build_client_from_configuration()
        try:
            instance = client.v2.service_instances.create(client.space_guid, 'test_name', client.plan_guid,
                                                       client.creation_parameters)
        except:
            return
        try:
            service_key = client.v2.service_keys.create(instance['metadata']['guid'], 'test_key_name')
            _logger.debug(service_key.json())
            client.v2.service_keys.remove(service_key['metadata']['guid'])
            _logger.debug("service key deleted")
        finally:
            try:
                client.v2.service_instances.remove(instance['metadata']['guid'])
            except:
                pass

    def test_get(self):
        client = build_client_from_configuration()
        cpt = 0
        for service_key in client.v2.service_keys.list():
            if cpt == 0:
                self.assertIsNotNone(
                    client.v2.service_keys.get_first(service_instance_guid=service_key['entity']['service_instance_guid']))
                self.assertIsNotNone(
                    client.v2.service_keys.get(service_key['metadata']['guid']))
            cpt += 1
        _logger.debug('test_get - %d found', cpt)
