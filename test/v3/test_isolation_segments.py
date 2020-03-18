import unittest
from http import HTTPStatus

from abstract_test_case import AbstractTestCase
from cloudfoundry_client.v3.entities import Entity, ToManyRelationship


class TestIsolationSegments(unittest.TestCase, AbstractTestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_client_class()

    def setUp(self):
        self.build_client()

    def test_list(self):
        self.client.get.return_value = self.mock_response('/v3/isolation_segments',
                                                          HTTPStatus.OK,
                                                          None,
                                                          'v3', 'isolation_segments', 'GET_response.json')
        all_isolation_segments = [isolation_segment for isolation_segment in self.client.v3.isolation_segments.list()]
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertEqual(5, len(all_isolation_segments))
        self.assertEqual(all_isolation_segments[0]['name'], "an_isolation_segment")
        self.assertIsInstance(all_isolation_segments[0], Entity)
        for isolation_segment in all_isolation_segments:
            self.assertIsInstance(isolation_segment, Entity)

    def test_get(self):
        self.client.get.return_value = self.mock_response(
            '/v3/isolation_segments/isolation_segment_id',
            HTTPStatus.OK,
            None,
            'v3', 'isolation_segments', 'GET_{id}_response.json')
        result = self.client.v3.isolation_segments.get('isolation_segment_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)

    def test_update(self):
        self.client.patch.return_value = self.mock_response(
            '/v3/isolation_segments/isolation_segment_id',
            HTTPStatus.OK,
            None,
            'v3', 'isolation_segments', 'PATCH_{id}_response.json')
        result = self.client.v3.isolation_segments.update('isolation_segment_id',
                                                          'new-name',
                                                          meta_labels=dict(key="value"))
        self.client.patch.assert_called_with(self.client.patch.return_value.url,
                                             json={
                                                 'name': 'new-name',
                                                 'metadata': {
                                                     'labels': {'key': 'value'},
                                                     'annotations': None
                                                 }
                                             })
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)

    def test_create(self):
        self.client.post.return_value = self.mock_response(
            '/v3/isolation_segments',
            HTTPStatus.OK,
            None,
            'v3', 'isolation_segments', 'POST_response.json')
        result = self.client.v3.isolation_segments.create('isolation_segment_id',
                                                          meta_labels=dict(key_label="value_label"),
                                                          meta_annotations=dict(key_annotation="value_annotation"))
        self.client.post.assert_called_with(self.client.post.return_value.url,
                                            files=None,
                                            json={'name': 'isolation_segment_id',
                                                  'metadata':
                                                      {
                                                          'labels': {'key_label': 'value_label'},
                                                          'annotations': {'key_annotation': 'value_annotation'}
                                                      }
                                                  })
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Entity)

    def test_remove(self):
        self.client.delete.return_value = self.mock_response(
            '/v3/isolation_segments/isolation_segment_id',
            HTTPStatus.NO_CONTENT,
            None)
        self.client.v3.isolation_segments.remove('isolation_segment_id')
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    def test_entitle_organizations(self):
        self.client.post.return_value = self.mock_response(
            '/v3/isolation_segments/isolation_segment_id/relationships/organizations',
            HTTPStatus.OK,
            None,
            'v3', 'isolation_segments', 'POST_{id}_relationships_organizations_response.json')
        result = self.client.v3.isolation_segments.entitle_organizations('isolation_segment_id', 'org_id_1', 'org_id_2')
        self.client.post.assert_called_with(self.client.post.return_value.url,
                                            files=None,
                                            json={
                                                'data': [
                                                    {'guid': 'org_id_1'},
                                                    {'guid': 'org_id_2'}
                                                ]
                                            })
        self.assertIsInstance(result, ToManyRelationship)
        self.assertEqual(2, len(result.guids))
        self.assertIsNotNone(result['links'])

    def test_revoke_organization(self):
        self.client.delete.return_value = self.mock_response(
            '/v3/isolation_segments/isolation_segment_id/relationships/organizations/org_id',
            HTTPStatus.NO_CONTENT,
            None)
        self.client.v3.isolation_segments.revoke_organization('isolation_segment_id', 'org_id')
        self.client.delete.assert_called_with(self.client.delete.return_value.url)

    def test_list_entitled_organizations(self):
        self.client.get.return_value = self.mock_response(
            '/v3/isolation_segments/isolation_segment_id/relationships/organizations',
            HTTPStatus.OK,
            None,
            'v3', 'isolation_segments', 'GET_{id}_relationships_organizations_response.json')
        result = self.client.v3.isolation_segments.list_entitled_organizations('isolation_segment_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsInstance(result, ToManyRelationship)
        self.assertEqual(2, len(result.guids))
        self.assertIsNotNone(result['links'])

    def test_list_entitled_spaces(self):
        self.client.get.return_value = self.mock_response(
            '/v3/isolation_segments/isolation_segment_id/relationships/spaces',
            HTTPStatus.OK,
            None,
            'v3', 'isolation_segments', 'GET_{id}_relationships_spaces_response.json')
        result = self.client.v3.isolation_segments.list_entitled_spaces('isolation_segment_id')
        self.client.get.assert_called_with(self.client.get.return_value.url)
        self.assertIsInstance(result, ToManyRelationship)
        self.assertEqual(2, len(result.guids))
        self.assertIsNotNone(result['links'])
