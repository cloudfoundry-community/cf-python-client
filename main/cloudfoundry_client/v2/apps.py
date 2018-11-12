import json
import logging
import os
from time import sleep

from cloudfoundry_client.errors import InvalidStatusCode
from cloudfoundry_client.imported import BAD_REQUEST
from cloudfoundry_client.json_object import JsonObject
from cloudfoundry_client.v2.entities import Entity, EntityManager

_logger = logging.getLogger(__name__)


class _Application(Entity):
    def instances(self):
        return self.client.v2.apps.get_instances(self['metadata']['guid'])

    def start(self):
        return self.client.v2.apps.start(self['metadata']['guid'])

    def stop(self):
        return self.client.v2.apps.stop(self['metadata']['guid'])

    def stats(self):
        return self.client.v2.apps.get_stats(self['metadata']['guid'])

    def summary(self):
        return self.client.v2.apps.get_summary(self['metadata']['guid'])

    def restage(self):
        return self.client.v2.apps.restage(self['metadata']['guid'])

    def recent_logs(self):
        return self.client.doppler.recent_logs(self['metadata']['guid'])

    def stream_logs(self):
        return self.client.doppler.stream_logs(self['metadata']['guid'])


class AppManager(EntityManager):
    APPLICATION_FIELDS = ['name', 'memory', 'instances', 'disk_quota', 'space_guid', 'stack_guid', 'state', 'command',
                          'buildpack', 'health_check_http_endpoint', 'health_check_type', 'health_check_timeout',
                          'diego', 'enable_ssh', 'docker_image', 'docker_credentials', 'environment_json', 'production',
                          'console', 'debug', 'staging_failed_reason', 'staging_failed_description', 'ports']

    def __init__(self, target_endpoint, client):
        super(AppManager, self).__init__(target_endpoint, client, '/v2/apps',
                                         lambda pairs: _Application(target_endpoint, client, pairs))

    def get_stats(self, application_guid):
        return self._get('%s/%s/stats' % (self.entity_uri, application_guid), JsonObject)

    def get_instances(self, application_guid):
        return self._get('%s/%s/instances' % (self.entity_uri, application_guid), JsonObject)

    def get_env(self, application_guid):
        return self._get('%s/%s/env' % (self.entity_uri, application_guid), JsonObject)

    def get_summary(self, application_guid):
        return self._get('%s/%s/summary' % (self.entity_uri, application_guid), JsonObject)

    def associate_route(self, application_guid, route_guid):
        self._put('%s%s/%s/routes/%s' % (self.target_endpoint, self.entity_uri, application_guid, route_guid))

    def list_routes(self, application_guid, **kwargs):
        return self.client.v2.routes._list('%s/%s/routes' % (self.entity_uri, application_guid), **kwargs)

    def remove_route(self, application_guid, route_guid):
        self._delete('%s%s/%s/routes/%s' % (self.target_endpoint, self.entity_uri, application_guid, route_guid))

    def list_service_bindings(self, application_guid, **kwargs):
        return self.client.v2.service_bindings._list('%s/%s/service_bindings' % (self.entity_uri, application_guid),
                                                     **kwargs)

    def start(self, application_guid, check_time=0.5, timeout=300, asynchronous=False):
        result = super(AppManager, self)._update(application_guid,
                                                 dict(state='STARTED'))
        if asynchronous:
            return result
        else:
            summary = self.get_summary(application_guid)
            self._wait_for_instances_in_state(application_guid, summary['instances'], 'RUNNING', check_time, timeout)
            return result

    def stop(self, application_guid, check_time=0.5, timeout=500, asynchronous=False):
        result = super(AppManager, self)._update(application_guid, dict(state='STOPPED'))
        if asynchronous:
            return result
        else:
            self._wait_for_instances_in_state(application_guid, 0, 'STOPPED', check_time, timeout)
            return result

    def restage(self, application_guid):
        return self._post("%s%s/%s/restage" % (self.target_endpoint, self.entity_uri, application_guid))

    def create(self, **kwargs):
        if kwargs.get('name') is None or kwargs.get('space_guid') is None:
            raise AssertionError('Please provide a name and a space_guid')
        request = AppManager._generate_application_update_request(**kwargs)
        return super(AppManager, self)._create(request)

    def update(self, application_guid, **kwargs):
        request = AppManager._generate_application_update_request(**kwargs)
        return super(AppManager, self)._update(application_guid, request)

    def remove(self, application_guid):
        super(AppManager, self)._remove(application_guid)

    def upload(self, application_guid, resources, application, asynchronous=False):
        application_size = os.path.getsize(application)
        with open(application, 'rb') as binary_file:
            return self.client.put("%s%s/%s/bits" % (self.target_endpoint, self.entity_uri, application_guid),
                                   params={"async": "true" if asynchronous else "false"} if asynchronous else None,
                                   data=dict(resources=json.dumps(resources)),
                                   files=dict(application=('application.zip',
                                                           binary_file,
                                                           'application/zip',
                                                           {'Content-Length': application_size,
                                                            'Content-Transfer-Encoding': 'binary'}))) \
                .json(object_pairs_hook=JsonObject)

    @staticmethod
    def _generate_application_update_request(**kwargs):
        return {key: kwargs[key] for key in AppManager.APPLICATION_FIELDS if key in kwargs}

    def _wait_for_instances_in_state(self, application_guid, number_required, state_expected, check_time, timeout):
        all_in_expected_state = False
        sum_waiting = 0
        while not all_in_expected_state:
            instances = self._safe_get_instances(application_guid)
            number_in_expected_state = 0
            for instance_number, instance in list(instances.items()):
                if instance['state'] == state_expected:
                    number_in_expected_state += 1
            # this case will make this code work for both stop and start operation
            all_in_expected_state = number_in_expected_state == number_required
            if not all_in_expected_state:
                _logger.debug('_wait_for_instances_in_state - %d/%d %s', number_in_expected_state,
                              number_required,
                              state_expected)
                if sum_waiting > timeout:
                    raise AssertionError('Failed to get state %s for %d instances' % (state_expected, number_required))
                sleep(check_time)
                sum_waiting += check_time

    def _safe_get_instances(self, application_guid):
        try:
            return self.get_instances(application_guid)
        except InvalidStatusCode as ex:
            if ex.status_code == BAD_REQUEST and type(ex.body) == dict:
                code = ex.body.get('code', -1)
                # 170002: staging not finished
                # 220001: instances error
                if code == 220001 or code == 170002:
                    return {}
                else:
                    _logger.error("")
            raise
