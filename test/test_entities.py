import unittest

from cloudfoundry_client.entities import EntityManager
from cloudfoundry_client.imported import OK, reduce
from fake_requests import TARGET_ENDPOINT, mock_response
from imported import MagicMock, call


class TestEntities(unittest.TestCase):
    def test_query(self):
        url = EntityManager._get_url_filtered('/v2/apps', **{"results-per-page": 20,
                                                             'order-direction': 'asc',
                                                             'page': 1,
                                                             "space_guid": 'some-id'})
        self.assertEqual('/v2/apps?order-direction=asc&page=1&results-per-page=20&q=space_guid%20IN%20some-id', url)

    def test_list(self):
        client = MagicMock()
        entity_manager = EntityManager(TARGET_ENDPOINT, client, '/fake/first')

        first_response = mock_response(
            '/fake/first?order-direction=asc&page=1&results-per-page=20&q=space_guid%20IN%20some-id',
            OK,
            None,
            'fake', 'GET_multi_page_0_response.json')
        second_response = mock_response('/fake/next?order-direction=asc&page=2&results-per-page=50',
                                        OK,
                                        None,
                                        'fake', 'GET_multi_page_1_response.json')

        client.get.side_effect = [first_response, second_response]
        cpt = reduce(lambda increment, _: increment + 1, entity_manager.list(**{"results-per-page": 20,
                                                                                'order-direction': 'asc',
                                                                                'page': 1,
                                                                                "space_guid": 'some-id'}), 0)
        client.get.assert_has_calls([call(first_response.url),
                                     call(second_response.url)],
                                    any_order=False)
        self.assertEqual(cpt, 3)

    def test_iter(self):
        client = MagicMock()
        entity_manager = EntityManager(TARGET_ENDPOINT, client, '/fake/something')

        client.get.return_value = mock_response(
            '/fake/something',
            OK,
            None,
            'fake', 'GET_response.json')
        cpt = reduce(lambda increment, _: increment + 1, entity_manager, 0)
        client.get.assert_called_with(client.get.return_value.url)

        self.assertEqual(cpt, 2)

    def test_get_elem(self):
        client = MagicMock()
        entity_manager = EntityManager(TARGET_ENDPOINT, client, '/fake/something')

        client.get.return_value = mock_response(
            '/fake/something/with-id',
            OK,
            None,
            'fake', 'GET_{id}_response.json')
        entity = entity_manager['with-id']
        client.get.assert_called_with(client.get.return_value.url)

        self.assertEqual(entity['entity']['name'], 'name-423')
