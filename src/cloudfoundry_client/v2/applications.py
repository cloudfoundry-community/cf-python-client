import json
import httplib
import logging
from time import sleep

from cloudfoundry_client.calls import InvalidStatusCode
from cloudfoundry_client.entities import EntityManager

_logger = logging.getLogger(__name__)


class ApplicationsManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(ApplicationsManager, self).__init__(target_endpoint, credentials_manager, '/v2/apps')

    def get_stats(self, application_guid):
        return super(ApplicationsManager, self).get(application_guid, 'stats')

    def get_instances(self, application_guid):
        return super(ApplicationsManager, self).get(application_guid, 'instances')

    def get_env(self, application_guid):
        return super(ApplicationsManager, self).get(application_guid, 'env')

    def start(self, application_guid, check_time=0.5):
        result = super(ApplicationsManager, self)._update(application_guid,
                                                          dict(state='STARTED'))
        all_running = False
        while not all_running:
            sleep(check_time)
            all_running = True
            instances = self.get_instances(application_guid)
            _logger.debug('start - %s', json.dumps(instances))
            for instance_number, instance in instances.items():
                if instance['state'] != 'RUNNING':
                    all_running = False
                    if instance['state'] != 'STARTING':
                        raise InvalidStatusCode(httplib.BAD_REQUEST,
                                                'Invalid application status %s' % instance['state'])
        return result

    def stop(self, application_guid, check_time=0.5):
        result = super(ApplicationsManager, self)._update(application_guid, dict(state='STOPPED'))
        some_running = True
        while some_running:
            sleep(check_time)
            try:
                instances = self.get_instances(application_guid)
                _logger.debug('stop - %s', json.dumps(instances))
            except InvalidStatusCode, ex:
                if ex.status_code == httplib.BAD_REQUEST:
                    some_running = False
        return result



