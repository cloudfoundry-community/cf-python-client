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
