import httplib
import unittest

import mock

from cloudfoundry_client.v2.service_plans import ServicePlanManager
from fake_requests import mock_response, TARGET_ENDPOINT


class TestServicePlans(unittest.TestCase):
    def setUp(self):
        self.credential_manager = mock.MagicMock()
        self.service_plans = ServicePlanManager(TARGET_ENDPOINT, self.credential_manager)

    def test_list(self):
        self.credential_manager.get.return_value = mock_response(
            '/v2/service_plans?q=service_guid%20IN%20service_id',
            httplib.OK,
            None,
            'v2', 'service_plans', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1, self.service_plans.list(service_guid='service_id'), 0)
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertEqual(cpt, 1)

    def test_get(self):
        self.credential_manager.get.return_value = mock_response(
            '/v2/service_plans/plan_id',
            httplib.OK,
            None,
            'v2', 'service_plans', 'GET_{id}_response.json')
        result = self.service_plans.get('plan_id')
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertIsNotNone(result)

    def test_list_instances(self):
        self.credential_manager.get.return_value = mock_response(
            '/v2/service_plans/plan_id/service_instances?q=space_guid%20IN%20space_id',
            httplib.OK,
            None,
            'v2', 'apps', 'GET_{id}_routes_response.json')
        cpt = reduce(lambda increment, _: increment + 1,
                     self.service_plans.list_instances('plan_id', space_guid='space_id'), 0)
        self.credential_manager.get.assert_called_with(self.credential_manager.get.return_value.url)
        self.assertEqual(cpt, 1)
