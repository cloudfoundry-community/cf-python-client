from config_test import build_client_from_configuration
import unittest
import logging
import json

_logger = logging.getLogger(__name__)



class TestServicePlan(unittest.TestCase):
    def test_list_instance_for_plan(self):
        client = build_client_from_configuration()
        for instance in client.service_plan.list_instance(client.plan_guid, space_guid=client.space_guid):
            _logger.debug('test instance list - %s -%s', instance['metadata']['guid'], instance['entity']['name'])