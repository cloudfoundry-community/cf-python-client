from config_test import build_client_from_configuration
import unittest
import logging
import json

_logger = logging.getLogger(__name__)


class TestServices(unittest.TestCase):
    def test_list_services(self):
        cpt = 0
        client = build_client_from_configuration()
        for service in client.service.list():
            _logger.debug('- %s' % service['entity']['label'])
            if cpt == 0:
                service = client.service.get_first(label=service['entity']['label'])
                self.assertIsNotNone(service)
            cpt += 1

        _logger.debug('test service list - %d found', cpt)

    def test_list_plans(self):
        cpt = 0
        client = build_client_from_configuration()
        for plan in client.service_plan.list(service_guid=client.service_guid):
            if cpt == 0:
                _logger.debug(json.dumps(plan))
            cpt += 1
        _logger.debug('test plan list - %d found', cpt)

    def test_all(self):
        client = build_client_from_configuration()
        binding_by_app = {}
        for instance in client.service_instance.list(space_guid=client.space_guid):
            self.assertIsNotNone(
                client.service_instance.get_first(space_guid=client.space_guid, name=instance['entity']['name']))
            for binding in client.service_binding.list(service_instance_guid=instance['metadata']['guid']):
                binding_reloaded = client.service_binding.get(binding['metadata']['guid'])
                self.assertIsNotNone(binding_reloaded)
                binding_by_app[binding['entity']['app_guid']] = binding_by_app.get(binding['entity']['app_guid'],
                                                                                   0) + 1
        for application in client.application.list(space_guid=client.space_guid):
            cpt = 0
            for _ in client.service_binding.list(app_guid=application['metadata']['guid']):
                cpt += 1
            self.assertEqual(cpt, binding_by_app.get(application['metadata']['guid'], 0))

    def test_create_update_delete(self):
        client = build_client_from_configuration()
        result = client.service_instance.create(client.space_guid, 'test_name', client.plan_guid,
                                                client.creation_parameters)
        result_updated = client.service_instance.update(result['metadata']['guid'], client.creation_parameters)
        _logger.debug(json.dumps(result_updated))
        client.service_instance.remove(result['metadata']['guid'])

    def test_create_bind_unbind_delete(self):

        client = build_client_from_configuration()
        instance = client.service_instance.create(client.space_guid, 'test_name', client.plan_guid,
                                                  client.creation_parameters)
        try:
            binding = client.service_binding.create(client.app_guid, instance['metadata']['guid'])
            _logger.debug(json.dumps(binding))
            client.service_binding.remove(binding['metadata']['guid'])
            _logger.debug("binding deleted")
        finally:
            client.service_instance.remove(instance['metadata']['guid'])