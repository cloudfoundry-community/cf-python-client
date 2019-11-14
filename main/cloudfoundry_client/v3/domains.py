from cloudfoundry_client.v3.entities import EntityManager


class DomainManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(DomainManager, self).__init__(target_endpoint, client, '/v3/domains')

    def create(self, name, internal=False, organization=None, shared_organizations=None,
               meta_labels=None, meta_annotations=None):
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

    def list_domains_for_org(self, org_guid, **kwargs):
        uri = '{entity}/{guid}/domains'.format(entity=self.entity_uri,
                                               guid=org_guid)
        return self._list(uri, **kwargs)

    def update(self, domain_guid, meta_labels=None, meta_annotations=None):
        data = {
            'metadata': {
                'labels': meta_labels,
                'annotations': meta_annotations
            }
        }
        return super(DomainManager, self)._update(domain_guid, data)

    def remove(self, domain_guid):
        super(DomainManager, self)._remove(domain_guid)

    def __create_shared_domain_url(self, domain_guid):
        # TODO use url parser for this
        return '{endpoint}{entity}/{domain}/relationships/shared_organizations' \
               ''.format(endpoint=self.target_endpoint, entity=self.entity_uri,
                         domain=domain_guid)

    def share_domain(self, domain_guid, organization_guids):
        if type(organization_guids) is not list():
            organization_guids = [organization_guids]
        url = self.__create_shared_domain_url(domain_guid)
        data = []
        for org in organization_guids:
            data.append({'guid': org})
        return super(DomainManager, self)._post(url, data=data)

    def unshare_domain(self, domain_guid, org_guid):
        url = '{uri}/{org}'.format(uri=self.__create_shared_domain_url(domain_guid),
                                   org=org_guid)
        super(DomainManager, self)._delete(url)
