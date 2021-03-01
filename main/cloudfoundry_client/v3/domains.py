from typing import Optional, TYPE_CHECKING

from cloudfoundry_client.v3.entities import EntityManager, ToOneRelationship, ToManyRelationship, PaginateEntities, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class Domain(Entity):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient", **kwargs):
        super(Domain, self).__init__(target_endpoint, client, **kwargs)
        relationships = self["relationships"]
        if "organization" in relationships:
            self["relationships"]["organization"] = ToOneRelationship.from_json_object(relationships["organization"])
        if "shared_organizations" in relationships:
            self["relationships"]["shared_organizations"] = ToManyRelationship.from_json_object(
                relationships["shared_organizations"]
            )


class DomainManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(DomainManager, self).__init__(target_endpoint, client, "/v3/domains", Domain)

    def create(
        self,
        name: str,
        internal: Optional[bool] = False,
        organization: Optional[ToOneRelationship] = None,
        shared_organizations: Optional[ToManyRelationship] = None,
        meta_labels: Optional[dict] = None,
        meta_annotations: Optional[dict] = None,
    ) -> Domain:
        data = {
            "name": name,
            "internal": internal,
            "organization": organization,
            "shared_organizations": shared_organizations,
            "metadata": {"labels": meta_labels, "annotations": meta_annotations},
        }
        return super(DomainManager, self)._create(data)

    def list_domains_for_org(self, org_guid: str, **kwargs) -> PaginateEntities:
        uri = "/v3/organizations/{guid}/domains".format(guid=org_guid)
        return self._list(uri, **kwargs)

    def update(self, domain_guid: str, meta_labels: Optional[dict] = None, meta_annotations: Optional[dict] = None) -> Domain:
        data = {"metadata": {"labels": meta_labels, "annotations": meta_annotations}}
        return super(DomainManager, self)._update(domain_guid, data)

    def remove(self, domain_guid: str):
        super(DomainManager, self)._remove(domain_guid)

    def __create_shared_domain_url(self, domain_guid: str) -> str:
        # TODO use url parser for this
        return "{endpoint}{entity}/{domain}/relationships/shared_organizations" "".format(
            endpoint=self.target_endpoint, entity=self.entity_uri, domain=domain_guid
        )

    def share_domain(self, domain_guid: str, organization_guids: ToManyRelationship) -> ToManyRelationship:
        url = self.__create_shared_domain_url(domain_guid)
        return ToManyRelationship.from_json_object(super(DomainManager, self)._post(url, data=organization_guids))

    def unshare_domain(self, domain_guid: str, org_guid: str):
        url = "{uri}/{org}".format(uri=self.__create_shared_domain_url(domain_guid), org=org_guid)
        super(DomainManager, self)._delete(url)
