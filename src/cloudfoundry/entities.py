class EntityManager(object):
    def __init__(self, target_endpoint, credentials_manager):
        self.target_endpoint = target_endpoint
        self.credentials_manager = credentials_manager

    def _list(self, url, **kwargs):
        response = self.credentials_manager.get(url, **kwargs)
        while True:
            for resource in response['resources']:
                yield resource
            if response['next_url'] is None:
                break
            else:
                response = self.credentials_manager.get(response['next_url'], **kwargs)
