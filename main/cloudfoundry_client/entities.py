import functools
import json
import logging

from urllib import quote

_logger = logging.getLogger(__name__)


class JsonObject(dict):
    def __init__(self, *args, **kwargs):
        super(JsonObject, self).__init__(*args, **kwargs)

    json = json.dumps


class Entity(JsonObject):
    def __init__(self, target_endpoint, client, *args, **kwargs):
        super(Entity, self).__init__(*args, **kwargs)
        self.target_endpoint = target_endpoint
        self.client = client
        try:
            for attribute, value in self['entity'].items():
                domain_name, suffix = attribute.rpartition('_')[::2]
                if suffix == 'url':
                    manager_name = domain_name if domain_name.endswith('s') else '%ss' % domain_name
                    try:
                        other_manager = getattr(client, manager_name)
                    except AttributeError:
                        # generic manager

                        other_manager = EntityManager(
                            target_endpoint,
                            client,
                            '')
                    if domain_name.endswith('s'):
                        new_method = functools.partial(other_manager._list, value)
                    else:
                        new_method = functools.partial(other_manager._get, value)
                    new_method.__name__ = domain_name
                    setattr(self, domain_name, new_method)
        except KeyError:
            print self.keys()
            raise


class InvalidStatusCode(Exception):
    def __init__(self, status_code, body):
        self.status_code = status_code
        self.body = body

    def __str__(self):
        if self.body is None:
            return '%d' % self.status_code
        elif type(self.body) == str:
            return '%d : %s' % (self.status_code, self.body)
        else:
            return '%d : %s' % (self.status_code, json.dumps(self.body))


class EntityManager(object):
    def __init__(self, target_endpoint, client, entity_uri, entity_builder=None):
        self.target_endpoint = target_endpoint
        self.entity_uri = entity_uri
        self.client = client
        self.entity_builder = entity_builder if entity_builder is not None else lambda pairs: Entity(target_endpoint,
                                                                                                     client, pairs)

    def _get(self, requested_path, entity_builder=None):
        url = '%s%s' % (self.target_endpoint, requested_path)
        response = EntityManager._check_response(self.client.get(url))
        _logger.debug('GET - %s - %s', requested_path, response.text)
        return self._read_response(response, entity_builder)

    def _list(self, requested_path, entity_builder=None, **kwargs):
        url_requested = EntityManager._get_url_filtered('%s%s' % (self.target_endpoint, requested_path), **kwargs)
        response = EntityManager._check_response(self.client
                                                 .get(url_requested))
        entity_builder = self._get_entity_builder(entity_builder)
        while True:
            _logger.debug('GET - %s - %s', url_requested, response.text)
            response_json = self._read_response(response, JsonObject)
            for resource in response_json['resources']:
                yield entity_builder(resource.items())
            if response_json['next_url'] is None:
                break
            else:
                url_requested = '%s%s' % (self.target_endpoint, response_json['next_url'])
                response = EntityManager._check_response(self.client.get(url_requested))

    def _create(self, data):
        url = '%s%s' % (self.target_endpoint, self.entity_uri)
        response = EntityManager._check_response(self.client.post(url, json=data))
        _logger.debug('POST - %s - %s', url, response.text)
        return self._read_response(response)

    def _update(self, resource_id, data):
        url = '%s%s/%s' % (self.target_endpoint, self.entity_uri, resource_id)
        response = EntityManager._check_response(self.client.put(url, json=data))
        _logger.debug('PUT - %s - %s', url, response.text)
        return self._read_response(response)

    def _remove(self, resource_id):
        url = '%s%s/%s' % (self.target_endpoint, self.entity_uri, resource_id)
        response = EntityManager._check_response(self.client.delete(url))
        _logger.debug('DELETE - %s - %s', url, response.text)

    def __iter__(self):
        return self.list()

    def __getitem__(self, entity_guid):
        return self.get(entity_guid)

    def list(self, **kwargs):
        return self._list(self.entity_uri, **kwargs)

    def get_first(self, **kwargs):
        kwargs.setdefault('results-per-page', 1)
        for entity in self._list(self.entity_uri, **kwargs):
            return entity
        return None

    def get(self, entity_id, *extra_paths):
        if len(extra_paths) == 0:
            requested_path = '%s/%s' % (self.entity_uri, entity_id)
        else:
            requested_path = '%s/%s/%s' % (self.entity_uri, entity_id, '/'.join(extra_paths))
        return self._get(requested_path)

    def _read_response(self, response, other_entity_builder=None):
        entity_builder = self._get_entity_builder(other_entity_builder)
        result = response.json(object_pairs_hook=JsonObject)
        return entity_builder(result.items())

    def _get_entity_builder(self, entity_builder):
        if entity_builder is None:
            return self.entity_builder
        else:
            return entity_builder

    @staticmethod
    def _get_url_filtered(url, **kwargs):
        list_query_paramters = ['page', 'results-per-page', 'order-direction']

        def _append_encoded_parameter(parameters, args):
            parameter_name, parameter_value = args[0], args[1]
            if parameter_name in list_query_paramters:
                parameters.append('%s=%s' % (parameter_name, str(parameter_value)))
            else:
                parameters.append('q=%s' % quote('%s IN %s' % (parameter_name, str(parameter_value))))
            return parameters

        if len(kwargs) > 0:
            return '%s?%s' % (url,
                              "&".join(reduce(_append_encoded_parameter, kwargs.items(), [])))
        else:
            return url

    @staticmethod
    def _check_response(response):
        if response.status_code / 100 == 2:
            return response
        else:
            try:
                body = response.json()
            except Exception:
                body = response.text
            raise InvalidStatusCode(response.status_code, body)
