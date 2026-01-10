from typing import TYPE_CHECKING

from cloudfoundry_client.v3.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class ServiceOfferingsManager(EntityManager[Entity]):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super().__init__(target_endpoint, client, "/v3/service_offerings")

    def update(self, guid: str, meta_labels: dict | None = None, meta_annotations: dict | None = None) -> Entity:
        payload = dict()
        self._metadata(payload, meta_labels, meta_annotations)
        return super()._update(guid, payload)

    def remove(self, guid: str, purge: bool = False) -> None:
        url = f"{self.target_endpoint}{self.entity_uri}/{guid}"
        if purge:
            url += "?purge=true"
        super()._delete(url)
