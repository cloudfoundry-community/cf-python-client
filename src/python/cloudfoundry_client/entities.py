import json
import logging
from urllib import quote

_logger = logging.getLogger(__name__)


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
        self.base_url = '%s%s' % (target_endpoint, entity_uri)
        self.credentials_manager = credentials_manager

    def _get_one(self, url):
        return EntityManager._check_response(self.credentials_manager.get(url)).json()

    def _create(self, data):
        response = EntityManager._check_response(self.credentials_manager.post(self.base_url, json=data))
        _logger.debug('POST - %s - %s', self.base_url, response.text)
        return response.json()

    def _update(self, resource_id, data):
        response = EntityManager._check_response(self.credentials_manager.put('%s/%s' % (self.base_url, resource_id),
                                                                              json=data))
        _logger.debug('PUT - %s/%s - %s', self.base_url, resource_id, response.text)
        return response.json()

    def _remove(self, resource_id):
        response = EntityManager._check_response(
            self.credentials_manager.delete('%s/%s' % (self.base_url, resource_id)))
        _logger.debug('DELETE - %s/%s - %s', self.base_url, resource_id, response.text)

    def list(self, *extra_paths, **kwargs):
        if len(extra_paths) == 0:
            requested_path = self.base_url
        else:
            requested_path = '%s/%s' % (self.base_url, '/'.join(extra_paths))
        response = EntityManager._check_response(self.credentials_manager
                                                 .get(EntityManager._get_url_filtered(requested_path, **kwargs)))
        while True:
            _logger.debug('GET - %s - %s', self.base_url, response.text)
            response_json = response.json()
            for resource in response_json['resources']:
                yield resource
            if response_json['next_url'] is None:
                break
            else:
                response = EntityManager._check_response(self.credentials_manager.get(response_json['next_url']))

    def get_first(self, **kwargs):
        response = EntityManager._check_response(self.credentials_manager
                                                 .get(EntityManager._get_url_filtered(self.base_url, **kwargs)))
        _logger.debug('GET - %s - %s', self.base_url, response.text)
        response_json = response.json()
        if len(response_json['resources']) > 0:
            return response_json['resources'][0]
        else:
            return None

    def get(self, entity_id, *extra_paths):

        if len(extra_paths) == 0:
            requested_path = '%s/%s' % (self.base_url, entity_id)
        else:
            requested_path = '%s/%s/%s' % (self.base_url, entity_id, '/'.join(extra_paths))
        response = EntityManager._check_response(self.credentials_manager.get(requested_path))
        _logger.debug('GET - %s - %s', requested_path, response.text)
        return response.json()

    @staticmethod
    def _get_url_filtered(url, **kwargs):
        if len(kwargs) > 0:
            return '%s?%s' % (url,
                              "&".join('q=%s' % quote("%s IN %s" % (k, v)) for k, v in kwargs.items()))
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
