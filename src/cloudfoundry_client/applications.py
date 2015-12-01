import json
from urllib import quote
from cloudfoundry_client.entities import EntityManager


class ApplicationsManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(ApplicationsManager, self).__init__(target_endpoint, credentials_manager)

    def list(self, space_guid):
        for resource in super(ApplicationsManager, self)._list('%s/v2/spaces/%s/apps' % (self.target_endpoint,
                                                                                         space_guid)):
            yield resource

    def get_by_name(self, space_guid, name):
        query = quote('name:%s' % name)
        return super(ApplicationsManager, self)._get_first('%s/v2/spaces/%s/apps?q=%s' % (self.target_endpoint,
                                                                                          space_guid,
                                                                                          query))

    def get_by_id(self, application_guid):
        return super(ApplicationsManager, self)._get_one('%s/v2/apps/%s' % (self.target_endpoint, application_guid))

    def get_stats(self, application_guid):
        return super(ApplicationsManager, self)._get_one('%s/v2/apps/%s/stats' %
                                                         (self.target_endpoint, application_guid))

    def get_instances(self, application_guid):
        return super(ApplicationsManager, self)._get_one('%s/v2/apps/%s/instances' %
                                                         (self.target_endpoint, application_guid))

    def start(self, application_guid, async=False):
        return self.credentials_manager.put('%s/v2/apps/%s?stage_async=%s' %
                                            (self.target_endpoint, application_guid, json.dumps(async)),
                                            json=dict(state='STARTED'))

    def stop(self, application_guid, async=False):
        return self.credentials_manager.put('%s/v2/apps/%s?stage_async=%s' %
                                            (self.target_endpoint, application_guid, json.dumps(async)),
                                            json=dict(state='STOPPED'))


