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

    def _get_first(self, url, **kwargs):
        response = self.credentials_manager.get(url, **kwargs)
        if len(response['resources']) > 0:
            return response['resources'][0]
        else:
            return None

    def _get_one(self, url, **kwargs):
        return self.credentials_manager.get(url, **kwargs)
