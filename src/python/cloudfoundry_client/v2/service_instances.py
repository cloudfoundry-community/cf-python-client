from cloudfoundry_client.entities import JsonObject, Entity, EntityManager


class _ServiceInstance(Entity):
    def space(self):
        return self.client.space._get(self.entity.space_url)

    def service_bindings(self, **kwargs):
        return self.client.service_binding._list(self.entity.service_bindings_url, **kwargs)

    def routes(self, **kwargs):
        return self.client.route._list(self.entity.routes_url, **kwargs)

    def service_plan(self):
        return self.client.service_plan._get(self.entity.service_plan_url)


class ServiceInstanceManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(ServiceInstanceManager, self).__init__(target_endpoint, client, '/v2/service_instances',
                                                     lambda pairs: _ServiceInstance(client, pairs))

    def create(self, space_guid, instance_name, plan_guid, parameters=None, tags=None):
        request = dict(name=instance_name,
                       space_guid=space_guid,
                       service_plan_guid=plan_guid)
        if parameters is not None:
            request['parameters'] = parameters
        if tags is not None:
            request['tags'] = tags
        return super(ServiceInstanceManager, self)._create(request)

    def update(self, instance_guid, instance_name=None, plan_guid=None, parameters=None, tags=None):
        request = dict()
        if instance_name is not None:
            request['name'] = instance_name
        if plan_guid is not None:
            request['service_plan_guid'] = plan_guid
        if parameters is not None:
            request['parameters'] = parameters
        if tags is not None:
            request['tags'] = tags
        return super(ServiceInstanceManager, self)._update(instance_guid, request)

    def list_permissions(self, instance_guid):
        return super(ServiceInstanceManager, self)._get('%s/%s/permissions' % (self.entity_uri, instance_guid),
                                                        JsonObject)

    def remove(self, instance_guid):
        super(ServiceInstanceManager, self)._remove(instance_guid)
