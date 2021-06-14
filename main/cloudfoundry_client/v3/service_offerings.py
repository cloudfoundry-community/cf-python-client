from typing import TYPE_CHECKING, Optional

from cloudfoundry_client.v3.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class ServiceOfferingsManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(ServiceOfferingsManager, self).__init__(target_endpoint, client, "/v3/service_offerings")

    def update(self, guid: str, meta_labels: Optional[dict] = None, meta_annotations: Optional[dict] = None) -> Entity:
        payload = dict()
        if meta_labels or meta_annotations:
            metadata = dict()
            if meta_labels:
                metadata["labels"] = meta_labels
            if meta_annotations:
                metadata["annotations"] = meta_annotations
            payload["metadata"] = metadata
        return super(ServiceOfferingsManager, self)._update(guid, payload)

    def remove(self, guid: str, purge: bool = False) -> None:
        url = f"{self.target_endpoint}{self.entity_uri}/{guid}"
        if purge:
            url += "?purge=true"
        super(ServiceOfferingsManager, self)._delete(url)
