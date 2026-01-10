from typing import TYPE_CHECKING
from dataclasses import dataclass, asdict

from cloudfoundry_client.v3.entities import Entity, EntityManager, ToManyRelationship

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


@dataclass
class AppsQuota:
    total_memory_in_mb: int
    per_process_memory_in_mb: int
    total_instances: int
    per_app_tasks: int


@dataclass
class ServicesQuota:
    paid_services_allowed: bool
    total_service_instances: int
    total_service_keys: int


@dataclass
class RoutesQuota:
    total_routes: int
    total_reserved_ports: int


@dataclass
class DomainsQuota:
    total_domains: int


class OrganizationQuotaManager(EntityManager[Entity]):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super().__init__(target_endpoint, client, "/v3/organization_quotas")

    def create(
        self,
        name: str,
        apps_quota: AppsQuota | None = None,
        services_quota: ServicesQuota | None = None,
        routes_quota: RoutesQuota | None = None,
        domains_quota: DomainsQuota | None = None,
        assigned_organizations: ToManyRelationship | None = None,
    ) -> Entity:
        data = self._asdict(name, apps_quota, services_quota, routes_quota, domains_quota, assigned_organizations)
        return super()._create(data)

    def update(
        self,
        guid: str,
        name: str,
        apps_quota: AppsQuota | None = None,
        services_quota: ServicesQuota | None = None,
        routes_quota: RoutesQuota | None = None,
        domains_quota: DomainsQuota | None = None,
    ) -> Entity:
        data = self._asdict(name, apps_quota, services_quota, routes_quota, domains_quota)
        return super()._update(guid, data)

    def apply_to_organizations(self, guid: str, organizations: ToManyRelationship) -> ToManyRelationship:
        return ToManyRelationship.from_json_object(
            super()._post(
                "%s%s/%s/relationships/organizations" % (self.target_endpoint, self.entity_uri, guid), data=organizations
            )
        )

    def remove(self, guid: str, asynchronous: bool = True) -> str | None:
        return super()._remove(guid, asynchronous)

    def _asdict(
        self,
        name: str,
        apps_quota: AppsQuota | None = None,
        services_quota: ServicesQuota | None = None,
        routes_quota: RoutesQuota | None = None,
        domains_quota: DomainsQuota | None = None,
        assigned_organizations: ToManyRelationship | None = None,
    ):
        data = {"name": name}
        if apps_quota:
            data["apps"] = asdict(apps_quota)
        if services_quota:
            data["services"] = asdict(services_quota)
        if routes_quota:
            data["routes"] = asdict(routes_quota)
        if domains_quota:
            data["domains"] = asdict(domains_quota)
        if assigned_organizations:
            data["relationships"] = {"organizations": assigned_organizations}
        return data
