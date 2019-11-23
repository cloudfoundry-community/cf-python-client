from typing import Optional

from cloudfoundry_client.v3.entities import EntityManager, ToOneRelationship, ToManyRelationship, PaginateEntities, \
    Entity


class DomainManager(EntityManager):
    def __init__(self, target_endpoint: str, client: 'CloudfoundryClient'):
        super(DomainManager, self).__init__(target_endpoint, client, '/v3/domains')

    def create(self, name: str, internal: Optional[bool] = False,
               organization: Optional[ToOneRelationship] = None,
               shared_organizations: Optional[ToManyRelationship] = None,
               meta_labels: Optional[dict] = None, meta_annotations: Optional[dict] = None):
        data = {
            'name': name,
            'internal': internal,
            'organization': organization,
            'shared_organizations': shared_organizations,
            'metadata': {
                'labels': meta_labels,
                'annotations': meta_annotations
            }
        }
        return super(DomainManager, self)._create(data)

    def list_domains_for_org(self, org_guid: str, **kwargs) -> PaginateEntities:
        uri = '/v3/organizations/{guid}/domains'.format(guid=org_guid)
        return self._list(uri, **kwargs)

    def update(self, domain_guid: str,
               meta_labels: Optional[dict] = None, meta_annotations: Optional[dict] = None) -> Entity:
        data = {
            'metadata': {
                'labels': meta_labels,
                'annotations': meta_annotations
            }
        }
        return super(DomainManager, self)._update(domain_guid, data)

    def remove(self, domain_guid: str):
        super(DomainManager, self)._remove(domain_guid)

    def __create_shared_domain_url(self, domain_guid: str) -> str:
        # TODO use url parser for this
        return '{endpoint}{entity}/{domain}/relationships/shared_organizations' \
               ''.format(endpoint=self.target_endpoint, entity=self.entity_uri,
                         domain=domain_guid)

    def share_domain(self, domain_guid: str, organization_guids: ToManyRelationship):
        url = self.__create_shared_domain_url(domain_guid)
        return super(DomainManager, self)._post(url, data=organization_guids)

    def unshare_domain(self, domain_guid: str, org_guid: str):
        url = '{uri}/{org}'.format(uri=self.__create_shared_domain_url(domain_guid),
                                   org=org_guid)
        super(DomainManager, self)._delete(url)
