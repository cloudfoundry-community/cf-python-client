from typing import Optional, TYPE_CHECKING

from cloudfoundry_client.v3.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class BuildpackManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(BuildpackManager, self).__init__(target_endpoint, client, "/v3/buildpacks")

    def create(
        self,
        name: str,
        position: Optional[int] = 0,
        enabled: Optional[bool] = True,
        locked: Optional[bool] = False,
        stack: Optional[str] = None,
        meta_labels: Optional[dict] = None,
        meta_annotations: Optional[dict] = None,
    ) -> Entity:
        data = {
            "name": name,
            "position": position,
            "enabled": enabled,
            "locked": locked,
            "stack": stack,
            "metadata": {"labels": meta_labels, "annotations": meta_annotations},
        }
        return super(BuildpackManager, self)._create(data)

    def remove(self, buildpack_guid: str):
        super(BuildpackManager, self)._remove(buildpack_guid)

    def update(
        self,
        buildpack_guid: str,
        name: str,
        position: Optional[int] = 0,
        enabled: Optional[bool] = True,
        locked: Optional[bool] = False,
        stack: Optional[str] = None,
        meta_labels: Optional[dict] = None,
        meta_annotations: Optional[dict] = None,
    ) -> Entity:
        data = {
            "name": name,
            "position": position,
            "enabled": enabled,
            "locked": locked,
            "stack": stack,
            "metadata": {"labels": meta_labels, "annotations": meta_annotations},
        }
        return super(BuildpackManager, self)._update(buildpack_guid, data)

    def upload(self, buildpack_guid: str, buildpack_zip: str, asynchronous: bool = False) -> Entity:
        buildpack = super(BuildpackManager, self)._upload_bits(buildpack_guid, buildpack_zip)
        if not asynchronous:
            self.client.v3.jobs.wait_for_job_completion(buildpack.job()["guid"])
            buildpack_after_job = super(BuildpackManager, self).get(buildpack["guid"])
            buildpack_after_job["links"]["job"] = buildpack["links"]["job"]
            buildpack_after_job.job = buildpack.job
            return buildpack_after_job
        return buildpack
