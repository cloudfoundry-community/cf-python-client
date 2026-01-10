from typing import TYPE_CHECKING

from cloudfoundry_client.v3.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class BuildpackManager(EntityManager[Entity]):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super().__init__(target_endpoint, client, "/v3/buildpacks")

    def create(
        self,
        name: str,
        position: int | None = 0,
        enabled: bool | None = True,
        locked: bool | None = False,
        stack: str | None = None,
        meta_labels: dict | None = None,
        meta_annotations: dict | None = None,
    ) -> Entity:
        data = {
            "name": name,
            "position": position,
            "enabled": enabled,
            "locked": locked,
            "stack": stack,
        }
        self._metadata(data, meta_labels, meta_annotations)
        return super()._create(data)

    def remove(self, buildpack_guid: str, asynchronous: bool = True) -> str | None:
        return super()._remove(buildpack_guid, asynchronous)

    def update(
        self,
        buildpack_guid: str,
        name: str,
        position: int | None = 0,
        enabled: bool | None = True,
        locked: bool | None = False,
        stack: str | None = None,
        meta_labels: dict | None = None,
        meta_annotations: dict | None = None,
    ) -> Entity:
        data = {
            "name": name,
            "position": position,
            "enabled": enabled,
            "locked": locked,
            "stack": stack,
        }
        self._metadata(data, meta_labels, meta_annotations)
        return super()._update(buildpack_guid, data)

    def upload(self, buildpack_guid: str, buildpack_zip: str, asynchronous: bool = False) -> Entity:
        buildpack = super()._upload_bits(buildpack_guid, buildpack_zip)
        if not asynchronous:
            self.client.v3.jobs.wait_for_job_completion(buildpack.job()["guid"])
            buildpack_after_job = super().get(buildpack["guid"])
            buildpack_after_job["links"]["job"] = buildpack["links"]["job"]
            buildpack_after_job.job = buildpack.job
            return buildpack_after_job
        return buildpack
