from cloudfoundry_client.v3.entities import EntityManager


class FeatureFlagManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(FeatureFlagManager, self).__init__(target_endpoint, client, '/v3/feature_flags')

