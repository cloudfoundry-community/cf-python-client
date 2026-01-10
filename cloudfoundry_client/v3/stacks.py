from typing import TYPE_CHECKING

from cloudfoundry_client.common_objects import Pagination
from cloudfoundry_client.v3.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class StackMananager(EntityManager[Entity]):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super().__init__(target_endpoint, client, "/v3/stacks")

    def create(
            self,
            name: str,
            description: str | None = None,
            meta_labels: dict | None = None,
            meta_annotations: dict | None = None,
    ) -> Entity:
        data = {"name": name}
        if description is not None:
            data["description"] = description
        self._metadata(data, meta_labels, meta_annotations)
        return super()._create(data)

    def update(
            self,
            stack_guid: str,
            meta_labels: dict | None = None,
            meta_annotations: dict | None = None,
    ) -> Entity:
        data = {}
        self._metadata(data, meta_labels, meta_annotations)
        return super()._update(stack_guid, data)

    def list_apps(self, stack_guid: str, **kwargs) -> Pagination[Entity]:
        uri: str = "%s/%s/apps" % (self.entity_uri, stack_guid)
        return super()._list(requested_path=uri, **kwargs)

    def remove(self, stack_guid: str):
        super()._remove(stack_guid)
