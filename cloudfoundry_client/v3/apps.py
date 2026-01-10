from typing import TYPE_CHECKING

from cloudfoundry_client.common_objects import JsonObject, Pagination
from cloudfoundry_client.v3.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class AppManager(EntityManager[Entity]):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super().__init__(target_endpoint, client, "/v3/apps")

    def restart(self, application_guid: str):
        return super()._post("%s%s/%s/actions/restart" % (self.target_endpoint, self.entity_uri, application_guid))

    def remove(self, application_guid: str, asynchronous: bool = True) -> str | None:
        return super()._remove(application_guid, asynchronous)

    def get_env(self, application_guid: str) -> JsonObject:
        return super()._get("%s%s/%s/env" % (self.target_endpoint, self.entity_uri, application_guid))

    def list_routes(self, application_guid: str, **kwargs) -> Pagination[Entity]:
        uri: str = "%s/%s/routes" % (self.entity_uri, application_guid)
        return super()._list(requested_path=uri, **kwargs)

    def list_droplets(self, application_guid: str, **kwargs) -> Pagination[Entity]:
        uri: str = "%s/%s/droplets" % (self.entity_uri, application_guid)
        return super()._list(requested_path=uri, **kwargs)

    def get_manifest(self, application_guid: str) -> str:
        return self.client.get(url="%s%s/%s/manifest" % (self.target_endpoint, self.entity_uri, application_guid)).text

    def list_packages(self, application_guid: str, **kwargs) -> Pagination[Entity]:
        uri: str = "%s/%s/packages" % (self.entity_uri, application_guid)
        return super()._list(requested_path=uri, **kwargs)

    def list_revisions(self, application_guid: str, **kwargs) -> Pagination[Entity]:
        uri: str = "%s/%s/revisions" % (self.entity_uri, application_guid)
        return super()._list(requested_path=uri, **kwargs)

    def list_deployed_revisions(self, application_guid: str, **kwargs) -> Pagination[Entity]:
        uri: str = "%s/%s/revisions/deployed" % (self.entity_uri, application_guid)
        return super()._list(requested_path=uri, **kwargs)
