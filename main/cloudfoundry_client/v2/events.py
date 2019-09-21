from cloudfoundry_client.v2.entities import EntityManager


class EventManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(EventManager, self).__init__(target_endpoint, client, '/v2/events')

    def list_by_type(self, event_type):
        return self._list(self.entity_uri, type=event_type)
