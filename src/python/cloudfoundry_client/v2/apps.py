import httplib
import logging
from time import sleep

from cloudfoundry_client.entities import JsonObject, Entity, EntityManager, InvalidStatusCode

_logger = logging.getLogger(__name__)


class _Application(Entity):
    def instances(self):
        return self.client.apps.get_instances(self['metadata']['guid'])

    def start(self):
        return self.client.apps.start(self['metadata']['guid'])

    def stop(self):
        return self.client.apps.stop(self['metadata']['guid'])

    def stats(self):
        return self.client.apps.get_stats(self['metadata']['guid'])

    def summary(self):
        return self.client.apps.get_summary(self['metadata']['guid'])


class AppManager(EntityManager):
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

    def list_routes(self, application_guid, **kwargs):
        return self.client.routes._list('%s/%s/routes' % (self.entity_uri, application_guid), **kwargs)

    def list_service_bindings(self, application_guid, **kwargs):
        return self.client.service_bindings._list('%s/%s/service_bindings' % (self.entity_uri, application_guid),
                                                 **kwargs)

    def start(self, application_guid, check_time=0.5, timeout=300, async=False):
        result = super(AppManager, self)._update(application_guid,
                                                 dict(state='STARTED'))
        if async:
            return result
        else:
            summary = self.get_summary(application_guid)
            self._wait_for_instances_in_state(application_guid, summary['instances'], 'RUNNING', check_time, timeout)
            return result

    def stop(self, application_guid, check_time=0.5, timeout=500, async=False):
        result = super(AppManager, self)._update(application_guid, dict(state='STOPPED'))
        if async:
            return result
        else:
            self._wait_for_instances_in_state(application_guid, 0, 'STOPPED', check_time, timeout)
            return result

    def _wait_for_instances_in_state(self, application_guid, number_required, state_expected, check_time, timeout):
        all_in_expected_state = False
        sum_waiting = 0
        while not all_in_expected_state:
            instances = self._safe_get_instances(application_guid)
            number_in_expected_state = 0
            for instance_number, instance in instances.items():
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
        except InvalidStatusCode, ex:
            if ex.status_code == httplib.BAD_REQUEST and type(ex.body) == dict:
                code = ex.body.get('code', -1)
                # 170002: staging not finished
                # 220001: instances error
                if code == 220001 or code == 170002:
                    return {}
                else:
                    _logger.error("")
            raise
