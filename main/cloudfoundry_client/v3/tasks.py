from typing import Optional, TYPE_CHECKING

from cloudfoundry_client.v3.entities import EntityManager, Entity

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class TaskManager(EntityManager):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        super(TaskManager, self).__init__(target_endpoint, client, "/v3/tasks")

    def create(
        self,
        application_guid: str,
        command: str,
        name: Optional[str] = None,
        disk_in_mb: Optional[int] = None,
        memory_in_mb: Optional[int] = None,
        droplet_guid: Optional[str] = None,
    ) -> Entity:
        request = self._request(command=command)
        request["name"] = name
        request["disk_in_mb"] = disk_in_mb
        request["memory_in_mb"] = memory_in_mb
        request["droplet_guid"] = droplet_guid
        return self._post("%s/v3/apps/%s/tasks" % (self.target_endpoint, application_guid), data=request)

    def cancel(self, task_guid: str) -> Entity:
        return self._post("%s/v3/tasks/%s/actions/cancel" % (self.target_endpoint, task_guid))
