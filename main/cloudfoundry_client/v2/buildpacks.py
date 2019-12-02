from cloudfoundry_client.v2.entities import EntityManager, Entity


class BuildpackManager(EntityManager):
    def __init__(self, target_endpoint: str, client: 'CloudFoundryClient'):
        super(BuildpackManager, self).__init__(target_endpoint, client, '/v2/buildpacks')

    def update(self, buildpack_guid: str, parameters: dict) -> Entity:
        return super(BuildpackManager, self)._update(buildpack_guid, parameters)
