import logging
import unittest

from config_test import build_client_from_configuration

_logger = logging.getLogger(__name__)


class TestServicePlan(unittest.TestCase):
    def test_list_instance_for_plan(self):
        client = build_client_from_configuration()
        for instance in client.service_plans.list_instances(client.plan_guid, space_guid=client.space_guid):
            _logger.debug('test_list_instance_for_plan - %s -%s', instance['metadata']['guid'],
                          instance['entity']['name'])

    def test_list_by_broker(self):
        cpt = 0
        client = build_client_from_configuration()
        for plan in client.service_plans.list(service_broker_guid=client.service_guid):
            if cpt == 0:
                _logger.debug(plan.json())
            cpt += 1
        _logger.debug('test plan list - %d found', cpt)

    def test_list(self):
        cpt = 0
        client = build_client_from_configuration()
        for plan in client.service_plans.list():
            _logger.debug(plan.json())
            cpt += 1
        _logger.debug('test plan list - %d found', cpt)
