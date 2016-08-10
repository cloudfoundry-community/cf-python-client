import json
import logging
from urllib import quote

_logger = logging.getLogger(__name__)


class JsonObject(dict):
    def __init__(self, *args, **kwargs):
        super(JsonObject, self).__init__(*args, **kwargs)
        self.__dict__ = self


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
    def __init__(self, target_endpoint, credentials_manager, entity_uri):
        self.target_endpoint = target_endpoint
        self.base_url = '%s%s' % (target_endpoint, entity_uri)
        self.credentials_manager = credentials_manager

    def _get_one(self, url):
        return EntityManager._read_response(EntityManager._check_response(self.credentials_manager.get(url)))

    def _create(self, data):
        response = EntityManager._check_response(self.credentials_manager.post(self.base_url, json=data))
        _logger.debug('POST - %s - %s', self.base_url, response.text)
        return EntityManager._read_response(response)

    def _update(self, resource_id, data):
        response = EntityManager._check_response(self.credentials_manager.put('%s/%s' % (self.base_url, resource_id),
                                                                              json=data))
        _logger.debug('PUT - %s/%s - %s', self.base_url, resource_id, response.text)
        return EntityManager._read_response(response)

    def _remove(self, resource_id):
        response = EntityManager._check_response(
            self.credentials_manager.delete('%s/%s' % (self.base_url, resource_id)))
        _logger.debug('DELETE - %s/%s - %s', self.base_url, resource_id, response.text)

    def list(self, *extra_paths, **kwargs):
        if len(extra_paths) == 0:
            requested_path = self.base_url
        else:
            requested_path = '%s/%s' % (self.base_url, '/'.join(extra_paths))
        url_requested = EntityManager._get_url_filtered(requested_path, **kwargs)
        response = EntityManager._check_response(self.credentials_manager
                                                 .get(url_requested))
        while True:
            _logger.debug('GET - %s - %s', url_requested, response.text)
            response_json = EntityManager._read_response(response)
            for resource in response_json.resources:
                yield resource
            if response_json.next_url is None:
                break
            else:
                url_requested = '%s%s' % (self.target_endpoint, response_json.next_url)
                response = EntityManager._check_response(self.credentials_manager.get(url_requested))

    def get_first(self, **kwargs):
        response = EntityManager._check_response(self.credentials_manager
                                                 .get(EntityManager._get_url_filtered(self.base_url, **kwargs)))
        _logger.debug('GET - %s - %s', self.base_url, response.text)
        response_json = EntityManager._read_response(response)
        if len(response_json.resources) > 0:
            return response_json.resources[0]
        else:
            return None

    def get(self, entity_id, *extra_paths):

        if len(extra_paths) == 0:
            requested_path = '%s/%s' % (self.base_url, entity_id)
        else:
            requested_path = '%s/%s/%s' % (self.base_url, entity_id, '/'.join(extra_paths))
        response = EntityManager._check_response(self.credentials_manager.get(requested_path))
        _logger.debug('GET - %s - %s', requested_path, response.text)
        return EntityManager._read_response(response)

    @staticmethod
    def _get_url_filtered(url, **kwargs):
        list_query_paramters = ['page', 'results-per-page', 'order-direction']

        def _encode_query(parameter_name, parameter_value):
            if parameter_name in list_query_paramters:
                return '%s=%s' % (parameter_name, str(parameter_value))
            else:
                return '%s IN %s' % (parameter_name, str(parameter_value))

        if len(kwargs) > 0:
            query_parameters = []
            for parameter_name, parameter_value in kwargs.items():
                if parameter_name in list_query_paramters:
                    query_parameters.append('%s=%s' % (parameter_name, str(parameter_value)))
                else:
                    query_parameters.append('q=%s' % quote("%s IN %s" % (parameter_name, str(parameter_value))))
            return '%s?%s' % (url,
                              "&".join(query_parameters))
        else:
            return url

    @staticmethod
    def _check_response(response):
        if response.status_code / 100 == 2:
            return response
        else:
            try:
                body = response.json()
            except Exception, _:
                body = response.text
            raise InvalidStatusCode(response.status_code, body)

    @staticmethod
    def _read_response(response):
        def _to_attr_object(pairs):
            result = JsonObject()
            for k in pairs:
                result[k[0]] = k[1]
            return result

        return response.json(object_pairs_hook=_to_attr_object)
