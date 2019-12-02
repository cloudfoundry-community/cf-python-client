from typing import Optional

from cloudfoundry_client.v3.entities import EntityManager, Entity


class FeatureFlagManager(EntityManager):
    def __init__(self, target_endpoint: str, client: 'CloudfoundryClient'):
        super(FeatureFlagManager, self).__init__(target_endpoint, client, '/v3/feature_flags')

    def update(self, name: str, enabled: Optional[bool] = True, custom_error_message: Optional[str] = None) -> Entity:
        data = {
            'enabled': enabled,
            'custom_error_message': custom_error_message
        }
        return super(FeatureFlagManager, self)._update(name, data)
