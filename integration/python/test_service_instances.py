import logging
import unittest

from config_test import build_client_from_configuration

_logger = logging.getLogger(__name__)


class TestServiceInstances(unittest.TestCase):
    def test_create_update_delete(self):
        client = build_client_from_configuration()
        result = client.service_instances.create(client.space_guid, 'test_name', client.plan_guid,
                                                 client.creation_parameters)
        if len(client.update_parameters) > 0:
            result_updated = client.service_instances.update(result['metadata']['guid'], client.update_parameters)
        else:
            _logger.warning('update test skipped')
        client.service_instances.remove(result['metadata']['guid'])

    def test_get(self):
        client = build_client_from_configuration()
        cpt = 0
        for instance in client.service_instances.list():
            if cpt == 0:
                self.assertIsNotNone(
                    client.service_instances.get_first(space_guid=instance['entity']['space_guid']))
                self.assertIsNotNone(
                    client.service_instances.get(instance['metadata']['guid']))
                self.assertIsNotNone(
                    client.service_instances.list_permissions(instance['metadata']['guid']))
            cpt += 1
        _logger.debug('test_get - %d found', cpt)
