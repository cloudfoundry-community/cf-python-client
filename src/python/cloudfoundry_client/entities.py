from urllib import quote


class EntityManager(object):
    def __init__(self, target_endpoint, credentials_manager, entity_uri):
        self.base_url = '%s%s' % (target_endpoint, entity_uri)
        self.credentials_manager = credentials_manager

    def _get_one(self, url):
        return self.credentials_manager.get(url)

    def _create(self, data):
        return self.credentials_manager.post(self.base_url, data)

    def _update(self, resource_id, data):
        return self.credentials_manager.put('%s/%s' % (self.base_url, resource_id), data)

    def _remove(self, resource_id):
        self.credentials_manager.delete('%s/%s' % (self.base_url, resource_id))

    def list(self, **kwargs):
        response = self.credentials_manager.get(EntityManager._get_url_filtered(self.base_url, **kwargs))
        while True:
            for resource in response['resources']:
                yield resource
            if response['next_url'] is None:
                break
            else:
                response = self.credentials_manager.get(response['next_url'])

    def get_first(self, **kwargs):
        response = self.credentials_manager.get(EntityManager._get_url_filtered(self.base_url, **kwargs))
        if len(response['resources']) > 0:
            return response['resources'][0]
        else:
            return None

    def get(self, entity_id, *extra_paths):
        if len(extra_paths) == 0:
            return self.credentials_manager.get('%s/%s' % (self.base_url, entity_id))
        else:
            return self.credentials_manager.get('%s/%s/%s' % (self.base_url, entity_id, '/'.join(extra_paths)))

    @staticmethod
    def _get_url_filtered(url, **kwargs):
        if len(kwargs) > 0:
            return '%s?%s' % (url,
                              "&".join('q=%s' % quote("%s IN %s" % (k, v)) for k, v in kwargs.items()))
        else:
            return url
