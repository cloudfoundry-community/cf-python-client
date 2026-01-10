from typing import TYPE_CHECKING

from cloudfoundry_client.v3.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class FeatureFlagManager(EntityManager[Entity]):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super().__init__(target_endpoint, client, "/v3/feature_flags")

    def update(self, name: str, enabled: bool | None = True, custom_error_message: str | None = None) -> Entity:
        data = {"enabled": enabled, "custom_error_message": custom_error_message}
        return super()._update(name, data)
