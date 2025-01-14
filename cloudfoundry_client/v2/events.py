from typing import Generator, TYPE_CHECKING

from cloudfoundry_client.v2.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class EventManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(EventManager, self).__init__(target_endpoint, client, "/v2/events")

    def list_by_type(self, event_type: str) -> Generator[Entity, None, None]:
        return self._list(self.entity_uri, type=event_type)
