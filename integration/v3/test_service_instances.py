import logging
import unittest

from config_test import build_client_from_configuration

_logger = logging.getLogger(__name__)


class TestServiceInstances(unittest.TestCase):
    def test_create_delete(self):
        client = build_client_from_configuration()
        result = client.v3.service_instances.create(
            space_guid=client.space_guid,
            name="test_name",
            service_plan_guid=client.plan_guid,
            parameters=client.creation_parameters,
        )
        client.v3.jobs.wait_for_job_completion(result.job()["guid"])
        service_instance_guid = client.v3.service_instances.get_first(names="test_name")["guid"]
        client.v3.service_instances.remove(service_instance_guid)

    def test_get(self):
        client = build_client_from_configuration()
        cpt = 0
        for instance in client.v3.service_instances.list():
            if cpt == 0:
                self.assertIsNotNone(
                    client.v3.service_instances.get_first(space_guids=instance["relationships"]["space"]["data"]["guid"])
                )
                self.assertIsNotNone(client.v3.service_instances.get(instance["guid"]))
            cpt += 1
        _logger.debug("test_get - %d found", cpt)
