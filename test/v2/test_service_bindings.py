import unittest
import logging
import json

from config_test import build_client_from_configuration


_logger = logging.getLogger(__name__)


class TestServiceBinding(unittest.TestCase):
    def test_create_bind_unbind_delete(self):
        client = build_client_from_configuration()
        try:
            instance = client.service_instance.create(client.space_guid, 'test_name', client.plan_guid,
                                                      client.creation_parameters)
        except:
            return
        try:
            binding = client.service_binding.create(client.app_guid, instance['metadata']['guid'])
            _logger.debug(json.dumps(binding))
            client.service_binding.remove(binding['metadata']['guid'])
            _logger.debug("binding deleted")
        finally:
            try:
                client.service_instance.remove(instance['metadata']['guid'])
            except:
                pass

    def test_get(self):
        client = build_client_from_configuration()
        cpt = 0
        for binding in client.service_binding.list():
            if cpt == 0:
                _logger.debug(binding)
                self.assertIsNotNone(
                    client.service_binding.get_first(service_instance_guid=binding['entity']['service_instance_guid']))
                self.assertIsNotNone(
                    client.service_binding.get_first(app_guid=binding['entity']['app_guid']))
                self.assertIsNotNone(
                    client.service_binding.get(binding['metadata']['guid']))
            cpt += 1
        _logger.debug('test_get - %d found', cpt)
