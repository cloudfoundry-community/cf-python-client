from typing import TYPE_CHECKING

from cloudfoundry_client.v3.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class TaskManager(EntityManager[Entity]):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super().__init__(target_endpoint, client, "/v3/tasks")

    def create(
        self,
        application_guid: str,
        command: str,
        name: str | None = None,
        disk_in_mb: int | None = None,
        memory_in_mb: int | None = None,
        droplet_guid: str | None = None,
    ) -> Entity:
        request = self._request(command=command)
        request["name"] = name
        request["disk_in_mb"] = disk_in_mb
        request["memory_in_mb"] = memory_in_mb
        request["droplet_guid"] = droplet_guid
        return self._post("%s/v3/apps/%s/tasks" % (self.target_endpoint, application_guid), data=request)

    def cancel(self, task_guid: str) -> Entity:
        return self._post("%s/v3/tasks/%s/actions/cancel" % (self.target_endpoint, task_guid))
