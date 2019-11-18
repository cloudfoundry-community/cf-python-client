from cloudfoundry_client.v3.entities import EntityManager


class DomainManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(DomainManager, self).__init__(target_endpoint, client, '/v3/domains')

    def create(self, name: str, internal: bool = False, organization: str = None,
               shared_organizations: str = None, meta_labels: dict = None,
               meta_annotations: dict = None) -> 'Entity':
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

    def list_domains_for_org(self, org_guid: str, **kwargs):
        uri = '/v3/organizations/{guid}/domains'.format(guid=org_guid)
        return self._list(uri, **kwargs)

    def update(self, domain_guid: str, meta_labels: dict = None,
               meta_annotations: dict = None) -> 'Entity':
        data = {
            'metadata': {
                'labels': meta_labels,
                'annotations': meta_annotations
            }
        }
        return super(DomainManager, self)._update(domain_guid, data)

    def remove(self, domain_guid: str):
        super(DomainManager, self)._remove(domain_guid)

    def __create_shared_domain_url(self, domain_guid) -> str:
        # TODO use url parser for this
        return '{endpoint}{entity}/{domain}/relationships/shared_organizations' \
               ''.format(endpoint=self.target_endpoint, entity=self.entity_uri,
                         domain=domain_guid)

    def share_domain(self, domain_guid: str, organization_guids: str) -> 'Entity':
        if type(organization_guids) is not list():
            organization_guids = [organization_guids]
        url = self.__create_shared_domain_url(domain_guid)
        data = []
        for org in organization_guids:
            data.append({'guid': org})
        return super(DomainManager, self)._post(url, data=data)

    def unshare_domain(self, domain_guid: str, org_guid: str):
        url = '{uri}/{org}'.format(uri=self.__create_shared_domain_url(domain_guid),
                                   org=org_guid)
        super(DomainManager, self)._delete(url)
