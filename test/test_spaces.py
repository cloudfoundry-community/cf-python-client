from config_test import build_client_from_configuration
import unittest
import logging

_logger = logging.getLogger(__name__)


class TestSpaces(unittest.TestCase):
    def test_list(self):
        cpt = 0
        client = build_client_from_configuration()
        for space in client.space.list(client.org_guid):
            if cpt == 0:
                client.space.get_by_id(space['metadata']['guid'])
                space = client.space.get_by_name(client.org_guid, space['entity']['name'])
                if space is None:
                    raise AssertionError("error - space not found by name")
            cpt += 1
        _logger.debug('test spaces list - %d found', cpt)
