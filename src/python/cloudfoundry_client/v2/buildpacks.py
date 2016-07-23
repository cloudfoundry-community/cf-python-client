from cloudfoundry_client.entities import EntityManager


class BuildpackManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(BuildpackManager, self).__init__(target_endpoint, credentials_manager, '/v2/buildpacks')

    def update(self, buildpack_guid, parameters):
        return super(BuildpackManager, self)._update(buildpack_guid, parameters)