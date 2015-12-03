import json
from urllib import quote
from cloudfoundry_client.entities import EntityManager


class ServiceManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(ServiceManager, self).__init__(target_endpoint, credentials_manager)

    def list_services(self, space_guid):
        for resource in super(ServiceManager, self)._list('%s/v2/spaces/%s/services' % (self.target_endpoint,
                                                                                        space_guid)):
            yield resource

    def get_service_by_name(self, space_guid, service_name):
        query = quote('label:%s' % service_name)
        return super(ServiceManager, self)._get_first('%s/v2/spaces/%s/services?q=%s' % (self.target_endpoint,
                                                                                         space_guid, query))

    def list_plans(self, service_guid):
        query = quote('service_guid:%s' % service_guid)
        for resource in super(ServiceManager, self)._list('%s/v2/service_plans?q=%s' % (self.target_endpoint, query)):
            yield resource

    def create_instance(self, space_guid, instance_name, plan_guid, parameters):
        request = dict(name=instance_name,
                       space_guid=space_guid,
                       service_plan_guid=plan_guid,
                       parameters=parameters)
        return self.credentials_manager.post(
            '%s/v2/service_instances?accepts_incomplete=true' % self.target_endpoint,
            json=request)


    def list_instances(self, space_guid):
        for resource in super(ServiceManager, self)._list('%s/v2/spaces/%s/service_instances' % (self.target_endpoint,
                                                                                                 space_guid)):
            yield resource

    def get_instance_by_name(self, space_guid, instance_name):
        query = quote('name:%s' % instance_name)
        return super(ServiceManager, self)._get_first('%s/v2/spaces/%s/service_instances?q=%s' % (self.target_endpoint,
                                                                                                  space_guid,
                                                                                                  query))

    def update_instance(self, instance_guid, parameters):
        request = dict(parameters=parameters, tags=[])
        return self.credentials_manager.put(
            '%s/v2/service_instances/%s?accepts_incomplete=true' % (self.target_endpoint,
                                                                    instance_guid),
            json=request)


    def delete_instance(self, instance_guid, async=False):
        self.credentials_manager.delete('%s/v2/service_instances/%s?accepts_incomplete=true&async=%s' %
                                        (self.target_endpoint, instance_guid, json.dumps(async)))

    def bind_application(self, app_guid, instance_guid, parameters=None):
        request = dict(app_guid=app_guid,
                       service_instance_guid=instance_guid)
        if parameters is None:
            request['parameters'] = {}
        else:
            request['parameters'] = parameters
        return self.credentials_manager.post('%s/v2/service_bindings' % self.target_endpoint,
                                             json=request)

    def list_bindings_by_application(self, application_guid):
        for resource in super(ServiceManager, self)._list('%s/v2/apps/%s/service_bindings' % (self.target_endpoint,
                                                                                              application_guid)):
            yield resource

    def list_bindings_by_instance(self, instance_id):
        for resource in super(ServiceManager, self) \
                ._list('%s/v2/service_instances/%s/service_bindings' % (self.target_endpoint,
                                                                        instance_id)):
            yield resource

    def get_binding(self, instance_id, app_guid):
        query = quote('app_guid:%s' % app_guid)
        return super(ServiceManager, self)._get_first(
            '%s/v2/service_instances/%s/service_bindings?q=%s' % (self.target_endpoint, instance_id, query))

    def unbind_application(self, binding_id, async=False):
        self.credentials_manager.delete('%s/v2/service_bindings/%s?async=%s' %
                                        (self.target_endpoint, binding_id, json.dumps(async)))




