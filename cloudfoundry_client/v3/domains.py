from typing import TYPE_CHECKING

from cloudfoundry_client.common_objects import Pagination
from cloudfoundry_client.v3.entities import EntityManager, ToOneRelationship, ToManyRelationship, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class Domain(Entity):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient", **kwargs):
        super().__init__(target_endpoint, client, **kwargs)
        relationships = self["relationships"]
        if "organization" in relationships:
            self["relationships"]["organization"] = ToOneRelationship.from_json_object(relationships["organization"])
        if "shared_organizations" in relationships:
            self["relationships"]["shared_organizations"] = ToManyRelationship.from_json_object(
                relationships["shared_organizations"]
            )


class DomainManager(EntityManager[Domain]):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super().__init__(target_endpoint, client, "/v3/domains", Domain)

    def create(
        self,
        name: str,
        internal: bool | None = False,
        organization: ToOneRelationship | None = None,
        shared_organizations: ToManyRelationship | None = None,
        meta_labels: dict | None = None,
        meta_annotations: dict | None = None,
    ) -> Domain:
        data = {
            "name": name,
            "internal": internal,
            "relationships": {
                "organization": organization,
                "shared_organizations": shared_organizations,
            },
        }
        self._metadata(data, meta_labels, meta_annotations)
        return super()._create(data)

    def list_domains_for_org(self, org_guid: str, **kwargs) -> Pagination[Entity]:
        uri = "/v3/organizations/{guid}/domains".format(guid=org_guid)
        return self._list(uri, **kwargs)

    def update(self, domain_guid: str, meta_labels: dict | None = None, meta_annotations: dict | None = None) -> Domain:
        data = {"metadata": {"labels": meta_labels, "annotations": meta_annotations}}
        return super()._update(domain_guid, data)

    def remove(self, domain_guid: str, asynchronous: bool = True) -> str | None:
        return super()._remove(domain_guid, asynchronous)

    def __create_shared_domain_url(self, domain_guid: str) -> str:
        # TODO use url parser for this
        return "{endpoint}{entity}/{domain}/relationships/shared_organizations" "".format(
            endpoint=self.target_endpoint, entity=self.entity_uri, domain=domain_guid
        )

    def share_domain(self, domain_guid: str, organization_guids: ToManyRelationship) -> ToManyRelationship:
        url = self.__create_shared_domain_url(domain_guid)
        return ToManyRelationship.from_json_object(super()._post(url, data=organization_guids))

    def unshare_domain(self, domain_guid: str, org_guid: str):
        url = "{uri}/{org}".format(uri=self.__create_shared_domain_url(domain_guid), org=org_guid)
        super()._delete(url)
