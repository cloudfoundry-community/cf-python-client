from typing import TYPE_CHECKING

from cloudfoundry_client.v3.entities import EntityManager

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class ServiceCredentialBindingManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(ServiceCredentialBindingManager, self).__init__(target_endpoint, client,
                                                              "/v3/service_credential_bindings")
