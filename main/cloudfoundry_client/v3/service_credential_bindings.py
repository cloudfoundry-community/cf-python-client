from typing import TYPE_CHECKING, Optional

from cloudfoundry_client.v3.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class ServiceCredentialBinding(Entity):
    @staticmethod
    def _manager_method(link_name: str, link_method: str) -> Optional[str]:
        if (link_name == "details" or link_name == "parameters") and link_method == "get":
            return "_get"  # instead of _paginate
        return Entity._manager_method(link_name, link_method)


class ServiceCredentialBindingManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(ServiceCredentialBindingManager, self).__init__(target_endpoint, client,
                                                              "/v3/service_credential_bindings",
                                                              ServiceCredentialBinding)
