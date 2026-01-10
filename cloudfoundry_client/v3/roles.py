from typing import TYPE_CHECKING

from cloudfoundry_client.v3.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class RoleManager(EntityManager[Entity]):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super().__init__(target_endpoint, client, "/v3/roles")

    def remove(self, role_guid: str, asynchronous: bool = True) -> str | None:
        return super()._remove(role_guid, asynchronous)
