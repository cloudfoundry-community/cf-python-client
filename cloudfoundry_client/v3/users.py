from typing import TYPE_CHECKING

from cloudfoundry_client.v3.entities import Entity, EntityManager

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class UserManager(EntityManager[Entity]):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super().__init__(target_endpoint, client, "/v3/users")

    def create(
        self,
        user_info: str | tuple[str, str],
        meta_labels: dict | None = None,
        meta_annotations: dict | None = None,
    ) -> Entity:
        data = {}
        if isinstance(user_info, str):
            data["guid"] = user_info
        else:
            username, origin = user_info
            data["username"] = username
            data["origin"] = origin
        self._metadata(data, meta_labels, meta_annotations)
        return super()._create(data)

    def update(
            self,
            guid: str,
            meta_labels: dict | None = None,
            meta_annotations: dict | None = None,
    ) -> Entity:
        data = {}
        self._metadata(data, meta_labels, meta_annotations)
        return super()._update(guid, data)

    def remove(self, guid: str) -> str | None:
        return super()._remove(guid)
