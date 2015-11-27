from cloudfoundry.entities import EntityManager


class ServiceManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(ServiceManager, self).__init__(target_endpoint, credentials_manager)

    def list_instances(self, space):
        for resource in super(ServiceManager, self)._list('%s%s' % (self.target_endpoint,
                                                                    space['entity']['service_instances_url'])):
            yield resource

    def list_bindings(self, application):
        for resource in super(ServiceManager, self)._list('%s%s' % (self.target_endpoint,
                                                                    application['entity']['service_bindings_url'])):
            yield resource



