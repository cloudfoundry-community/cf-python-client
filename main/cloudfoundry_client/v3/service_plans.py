from typing import Dict, List, Optional, TYPE_CHECKING

from cloudfoundry_client.v3.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class ServicePlanManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(ServicePlanManager, self).__init__(target_endpoint, client, "/v3/service_plans")

    def update(
        self,
        guid: str,
        meta_labels: Optional[dict] = None,
        meta_annotations: Optional[dict] = None,
    ) -> Entity:
        payload = {"metadata": {}}

        if meta_labels:
            payload["metadata"]["labels"] = meta_labels
        if meta_annotations:
            payload["metadata"]["annotations"] = meta_annotations
        return super(ServicePlanManager, self)._update(guid, payload)

    def remove(self, guid: str):
        super(ServicePlanManager, self)._remove(guid)

    def get_visibility(self, service_plan_guid: str) -> Dict:
        return super(ServicePlanManager, self)._get(f"{self.target_endpoint}{self.entity_uri}/{service_plan_guid}/visibility")

    def update_visibility(self, service_plan_guid: str, type: str, organizations: Optional[List[dict]] = None) -> Dict:
        payload = {"type": type}
        if organizations:
            payload["organizations"] = organizations
        return super(ServicePlanManager, self)._patch(
            url=f"{self.target_endpoint}{self.entity_uri}/{service_plan_guid}/visibility", data=payload
        )

    def apply_visibility_to_extra_orgs(self, service_plan_guid: str, organizations: List[dict]) -> Dict:
        payload = {"type": "organization", "organizations": organizations}
        return super(ServicePlanManager, self)._post(
            url=f"{self.target_endpoint}{self.entity_uri}/{service_plan_guid}/visibility", data=payload, files=None
        )

    def remove_org_from_service_plan_visibility(self, service_plan_guid: str, org_guid: str):
        super(ServicePlanManager, self)._delete(
            url=f"{self.target_endpoint}{self.entity_uri}/{service_plan_guid}/visibility/{org_guid}"
        )
