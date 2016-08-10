import httplib
import logging
from time import sleep

from cloudfoundry_client.entities import EntityManager, InvalidStatusCode

_logger = logging.getLogger(__name__)


class ApplicationManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(ApplicationManager, self).__init__(target_endpoint, credentials_manager, '/v2/apps')

    def get_stats(self, application_guid):
        return super(ApplicationManager, self).get(application_guid, 'stats')

    def get_instances(self, application_guid):
        return super(ApplicationManager, self).get(application_guid, 'instances')

    def get_env(self, application_guid):
        return super(ApplicationManager, self).get(application_guid, 'env')

    def get_summary(self, application_guid):
        return super(ApplicationManager, self).get(application_guid, 'summary')

    def start(self, application_guid, check_time=0.5, timeout=300, async=False):
        result = super(ApplicationManager, self)._update(application_guid,
                                                         dict(state='STARTED'))
        if async:
            return result
        else:
            summary = self.get_summary(application_guid)
            self._wait_for_instances_in_state(application_guid, summary['instances'], 'RUNNING', check_time, timeout)
            return result

    def stop(self, application_guid, check_time=0.5, timeout=500, async=False):
        result = super(ApplicationManager, self)._update(application_guid, dict(state='STOPPED'))
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
                _logger.debug('_wait_for_instances_in_state - %d/%d %s' % (number_in_expected_state,
                                                                          number_required,
                                                                          state_expected))
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
