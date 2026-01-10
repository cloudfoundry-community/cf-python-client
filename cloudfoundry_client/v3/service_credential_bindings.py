from typing import TYPE_CHECKING

from cloudfoundry_client.v3.entities import EntityManager, Entity, ToOneRelationship

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class ServiceCredentialBindingManager(EntityManager[Entity]):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super().__init__(target_endpoint, client, "/v3/service_credential_bindings")

    def create(
            self,
            name: str,
            service_credential_binding_type: str,
            service_instance_guid: str,
            application_guid: str | None,
            parameters: dict | None,
            meta_labels: dict | None,
            meta_annotations: dict | None,
            asynchronous: bool = True,
    ) -> str | Entity | None:
        data = {
            "name": name,
            "type": service_credential_binding_type,
            "relationships": {"service_instance": ToOneRelationship(service_instance_guid)},
        }
        if application_guid:
            data["relationships"]["app"] = ToOneRelationship(application_guid)
        if parameters:
            data["parameters"] = parameters
        if meta_labels or meta_annotations:
            metadata = dict()
            if meta_labels:
                metadata["labels"] = meta_labels
            if meta_annotations:
                metadata["annotations"] = meta_annotations
            data["metadata"] = metadata
        url = "%s%s" % (self.target_endpoint, self.entity_uri)
        response = self.client.post(url, json=data)
        location = super()._location(response)
        if location:
            job_guid = super()._extract_job_guid(location)
            if asynchronous:
                return job_guid
            else:
                self.client.v3.jobs.wait_for_job_completion(job_guid)
                return None
        return super()._read_response(response, None)
