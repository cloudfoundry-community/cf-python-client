import logging
import functools
from cloudfoundry_client.imported import quote, reduce
from cloudfoundry_client.json_object import JsonObject
from cloudfoundry_client.request_object import Request

_logger = logging.getLogger(__name__)


class Entity(JsonObject):
    def __init__(self, client, entity_manager, *args, **kwargs):
        super(Entity, self).__init__(*args, **kwargs)
        try:
            def default_method(m, u):
                raise NotImplementedError('Unknown method %s for url %s' % (m, u))

            for link_name, link in self.get('links', {}).items():
                if link_name != 'self':
                    link_method = link.get('method', 'GET').lower()
                    new_method = None
                    ref = link['href']
                    if link_method== 'get':
                        new_method = functools.partial(entity_manager._paginate, ref) if link_name.endswith('s')\
                            else functools.partial(entity_manager._get, ref)
                    elif link_method == 'post':
                        new_method = functools.partial(entity_manager._post, ref)
                    elif link_method == 'put':
                        new_method = functools.partial(entity_manager._put, ref)
                    elif link_method == 'delete':
                        new_method = functools.partial(entity_manager._delete, ref)
                    else:
                        new_method = functools.partial(default_method, link_method, ref)
                    new_method.__name__ = link_name
                    setattr(self, link_name, new_method)
        except KeyError:
            raise


class EntityManager(object):
    def __init__(self, target_endpoint, client, entity_uri):
        self.target_endpoint = target_endpoint
        self.entity_uri = entity_uri
        self.client = client

    def _post(self, url, data=None):
        response = self.client.post(url, json=data)
        _logger.debug('POST - %s - %s', url, response.text)
        return self._read_response(response)

    def _get(self, url):
        response = self.client.get(url)
        _logger.debug('GET - %s - %s', url, response.text)
        return self._read_response(response)

    def _put(self, data, url):
        response = self.client.put(url, json=data)
        _logger.debug('PUT - %s - %s', url, response.text)
        return self._read_response(response)

    def _delete(self, url):
        response = self.client.delete(url)
        _logger.debug('DELETE - %s - %s', url, response.text)

    def _list(self, requested_path, **kwargs):
        url_requested = EntityManager._get_url_filtered('%s%s' % (self.target_endpoint, requested_path), **kwargs)
        for element in self._paginate(url_requested):
            yield element

    def _paginate(self, url_requested):
        response = self.client.get(url_requested)
        while True:
            _logger.debug('GET - %s - %s', url_requested, response.text)
            response_json = self._read_response(response)
            for resource in response_json['resources']:
                yield self._entity(resource)
            if 'next' not in response_json['pagination'] \
                    or response_json['pagination']['next'] is None \
                    or response_json['pagination']['next'].get('href') is None:
                break
            else:
                url_requested = response_json['pagination']['next']['href']
                response = self.client.get(url_requested)

    def _create(self, data):
        url = '%s%s' % (self.target_endpoint, self.entity_uri)
        return self._post(url, data)

    def _update(self, resource_id, data):
        url = '%s%s/%s' % (self.target_endpoint, self.entity_uri, resource_id)
        return self._put(data, url)

    def _remove(self, resource_id):
        url = '%s%s/%s' % (self.target_endpoint, self.entity_uri, resource_id)
        self._delete(url)

    def __iter__(self):
        return self.list()

    def __getitem__(self, entity_guid):
        return self.get(entity_guid)

    def list(self, **kwargs):
        return self._list(self.entity_uri, **kwargs)

    def get_first(self, **kwargs):
        kwargs.setdefault('per_page', 1)
        for entity in self._list(self.entity_uri, **kwargs):
            return entity
        return None

    def get(self, entity_id, *extra_paths):
        if len(extra_paths) == 0:
            requested_path = '%s%s/%s' % (self.target_endpoint, self.entity_uri, entity_id)
        else:
            requested_path = '%s%s/%s/%s' % (self.target_endpoint, self.entity_uri, entity_id, '/'.join(extra_paths))
        return self._get(requested_path)

    def _read_response(self, response):
        result = response.json(object_pairs_hook=JsonObject)
        return self._entity(result)

    @staticmethod
    def _request(**mandatory_parameters):
        return Request(**mandatory_parameters)

    def _entity(self, result):
        if 'guid' in result:
            return Entity(self.client, self, **result)
        else:
            return result

    @staticmethod
    def _get_url_filtered(url, **kwargs):
        def _append_encoded_parameter(parameters, args):
            parameter_name, parameter_value = args[0], args[1]
            if isinstance(parameter_value, (list, tuple)):
                parameters.append('%s=%s' % (parameter_name, quote(','.join(parameter_value))))
            else:
                parameters.append('%s=%s' % (parameter_name, quote(str(parameter_value))))
            return parameters

        if len(kwargs) > 0:
            return '%s?%s' % (url,
                              "&".join(reduce(_append_encoded_parameter, sorted(list(kwargs.items())), [])))
        else:
            return url
