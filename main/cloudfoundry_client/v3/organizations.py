from typing import Optional

from cloudfoundry_client.v3.entities import EntityManager, Entity


class OrganizationManager(EntityManager):
    def __init__(self, target_endpoint: str, client: 'CloudfoundryClient'):
        super(OrganizationManager, self).__init__(target_endpoint, client, '/v3/organizations')

    def create(self, name: str, suspended: bool,
               meta_labels: Optional[dict] = None,
               meta_annotations: Optional[dict] = None) -> Entity:
        data = {
            'name': name,
            'suspended': suspended,
            'metadata': {
                'labels': meta_labels,
                'annotations': meta_annotations
            }
        }
        return super(OrganizationManager, self)._create(data)

    def update(self, guid: str, name: str, suspended: Optional[bool],
               meta_labels: Optional[dict] = None,
               meta_annotations: Optional[dict] = None) -> Entity:
        data = {
            'name': name,
            'suspended': suspended,
            'metadata': {
                'labels': meta_labels,
                'annotations': meta_annotations
            }
        }
        return super(OrganizationManager, self)._update(guid, data)

    def remove(self, guid: str):
        super(OrganizationManager, self)._remove(guid)

    def assign_default_isolation_segment(self, org_guid: str, iso_seg_guid: str) -> Entity:
        url = '{endpoint}{entity}/{guid}/relationships/default_isolation_segment' \
              ''.format(endpoint=self.target_endpoint,
                        entity=self.entity_uri,
                        guid=org_guid)
        data = {
            "data": {
                "guid": iso_seg_guid
            }
        }
        return super(OrganizationManager, self)._patch(url, data)

    def get_default_isolation_segment(self, guid: str) -> Entity:
        return super(OrganizationManager, self).get(guid, 'relationships', 'default_isolation_segment')

    def get_default_domain(self, guid: str) -> Entity:
        return super(OrganizationManager, self).get(guid, 'domains', 'default')

    def get_usage_summary(self, guid: str) -> Entity:
        return super(OrganizationManager, self).get(guid, 'usage_summary')
