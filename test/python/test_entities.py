import httplib
import unittest

import mock

from cloudfoundry_client.entities import EntityManager
from fake_requests import TARGET_ENDPOINT, mock_response


class TestEntities(unittest.TestCase):
    def test_query(self):
        url = EntityManager._get_url_filtered('/v2/apps', **{"results-per-page": 20,
                                                             'order-direction': 'asc', 'page': 1,
                                                             "space_guid": 'some-id'})
        self.assertEqual(url, '/v2/apps?q=space_guid%20IN%20some-id&results-per-page=20&page=1&order-direction=asc')

    def test_list(self):
        credential_manager = mock.MagicMock()
        entity_manager = EntityManager(TARGET_ENDPOINT, credential_manager, '/fake/first')

        first_response = mock_response(
            '/fake/first?q=space_guid%20IN%20some-id&results-per-page=20&page=1&order-direction=asc',
            httplib.OK,
            None,
            'fake', 'GET_first_response.json')
        second_response = mock_response('/fake/next?order-direction=asc&page=2&results-per-page=50',
                                        httplib.OK,
                                        None,
                                        'fake', 'GET_next_response.json')

        credential_manager.get.side_effect = [first_response, second_response]
        cpt = reduce(lambda increment, _: increment + 1, entity_manager.list(**{"results-per-page": 20,
                                                                                'order-direction': 'asc',
                                                                                'page': 1,
                                                                                "space_guid": 'some-id'}), 0)
        credential_manager.get.assert_has_calls([mock.call(first_response.url),
                                                 mock.call(second_response.url)],
                                                any_order=False)
        self.assertEqual(cpt, 3)
