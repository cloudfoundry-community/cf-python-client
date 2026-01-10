from typing import TYPE_CHECKING

from cloudfoundry_client.v3.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class ServicePlanManager(EntityManager[Entity]):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super().__init__(target_endpoint, client, "/v3/service_plans")

    def update(
        self,
        guid: str,
        meta_labels: dict | None = None,
        meta_annotations: dict | None = None,
    ) -> Entity:
        payload = {"metadata": {}}
        self._metadata(payload, meta_labels, meta_annotations)
        return super()._update(guid, payload)

    def remove(self, guid: str):
        super()._remove(guid)

    def get_visibility(self, service_plan_guid: str) -> dict:
        return super()._get(f"{self.target_endpoint}{self.entity_uri}/{service_plan_guid}/visibility")

    # Updates a service plan visibility. It behaves similar to the POST service plan visibility endpoint but
    # this endpoint will REPLACE the existing list of organizations when the service plan is organization visible.
    def update_visibility(self, service_plan_guid: str, type: str, organizations: list[dict] | None = None) -> dict:
        payload = {"type": type}
        if organizations:
            payload["organizations"] = organizations
        return super()._patch(
            url=f"{self.target_endpoint}{self.entity_uri}/{service_plan_guid}/visibility", data=payload
        )

    # Applies a service plan visibility. It behaves similar to the PATCH service plan visibility endpoint but
    # this endpoint will APPEND to the existing list of organizations when the service plan is organization visible.
    def apply_visibility_to_extra_orgs(self, service_plan_guid: str, organizations: list[dict]) -> dict:
        payload = {"type": "organization", "organizations": organizations}
        return super()._post(
            url=f"{self.target_endpoint}{self.entity_uri}/{service_plan_guid}/visibility", data=payload, files=None
        )

    def remove_org_from_service_plan_visibility(self, service_plan_guid: str, org_guid: str):
        super()._delete(
            url=f"{self.target_endpoint}{self.entity_uri}/{service_plan_guid}/visibility/{org_guid}"
        )
