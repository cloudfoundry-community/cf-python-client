from typing import TYPE_CHECKING

from cloudfoundry_client.v3.entities import EntityManager

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class RoleManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(RoleManager, self).__init__(target_endpoint, client, "/v3/roles")

    def remove(self, role_guid: str):
        super(RoleManager, self)._remove(role_guid)
