from cloudfoundry_client.v3.entities import EntityManager


class FeatureFlagManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(FeatureFlagManager, self).__init__(target_endpoint, client, '/v3/feature_flags')

    def update(self, name, enabled=True, custom_error_message=None):
        data = {
            'enabled': enabled,
            'custom_error_message': custom_error_message
        }
        return super(FeatureFlagManager, self)._update(name, data)
