import json
from cloudfoundry.entities import EntityManager


class ApplicationsManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(ApplicationsManager, self).__init__(target_endpoint, credentials_manager)

    def list(self, space):
        return self.credentials_manager.get('%s%s' %
                                            (self.target_endpoint, space['entity']['apps_url']))

    def start(self, application, async=False):
        return self.credentials_manager.put('%s%s?stage_async=%s' %
                                            (self.target_endpoint, application['metadata']['url'], json.dumps(async)),
                                            json=dict(state='STARTED'))

    def stop(self, application, async=False):
        return self.credentials_manager.put('%s%s?stage_async=%s' %
                                            (self.target_endpoint, application['metadata']['url'], json.dumps(async)),
                                            json=dict(state='STOPPED'))


