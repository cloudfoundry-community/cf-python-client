import json
from cloudfoundry.entities import EntityManager


class ApplicationsManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(ApplicationsManager, self).__init__(target_endpoint, credentials_manager)

    def list(self, space_guid):
        for resource in super(ApplicationsManager, self)._list('%s/v2/spaces/%s/apps' % (self.target_endpoint,
                                                                                         space_guid)):
            yield resource

    def start(self, application_guid, async=False):
        return self.credentials_manager.put('%s/v2/apps/%s?stage_async=%s' %
                                            (self.target_endpoint, application_guid, json.dumps(async)),
                                            json=dict(state='STARTED'))

    def stop(self, application_guid, async=False):
        return self.credentials_manager.put('%s/v2/apps/%s?stage_async=%s' %
                                            (self.target_endpoint, application_guid, json.dumps(async)),
                                            json=dict(state='STOPPED'))


