from cloudfoundry_client.v3.entities import EntityManager


class TaskManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(TaskManager, self).__init__(target_endpoint, client, '/v3/tasks')

    def create(self, application_guid, command, name=None, disk_in_mb=None, memory_in_mb=None, droplet_guid=None):
        request = dict(command=command)
        if name is not None:
            request['name'] = name
        if disk_in_mb is not None:
            request['disk_in_mb'] = disk_in_mb
        if memory_in_mb is not None:
            request['memory_in_mb'] = memory_in_mb
        if droplet_guid is not None:
            request['droplet_guid'] = droplet_guid
        return self._post('%s/v3/apps/%s/tasks' % (self.target_endpoint, application_guid), data=request)

    def cancel(self, task_guid):
        return self._post('%s/v3/tasks/%s/actions/cancel' % (self.target_endpoint, task_guid))
