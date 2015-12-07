import json
import httplib
import logging
from urllib import quote
from time import sleep

from cloudfoundry_client.calls import InvalidStatusCode
from cloudfoundry_client.entities import EntityManager

_logger = logging.getLogger(__name__)


class ApplicationsManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(ApplicationsManager, self).__init__(target_endpoint, credentials_manager)

    def list(self, space_guid):
        for resource in super(ApplicationsManager, self)._list('%s/v2/spaces/%s/apps' % (self.target_endpoint,
                                                                                         space_guid)):
            yield resource

    def get_by_name(self, space_guid, name):
        query = quote('name:%s' % name)
        return super(ApplicationsManager, self)._get_first('%s/v2/spaces/%s/apps?q=%s' % (self.target_endpoint,
                                                                                          space_guid,
                                                                                          query))

    def get_by_id(self, application_guid):
        return super(ApplicationsManager, self)._get_one('%s/v2/apps/%s' % (self.target_endpoint, application_guid))

    def get_stats(self, application_guid):
        return super(ApplicationsManager, self)._get_one('%s/v2/apps/%s/stats' %
                                                         (self.target_endpoint, application_guid))

    def get_instances(self, application_guid):
        return super(ApplicationsManager, self)._get_one('%s/v2/apps/%s/instances' %
                                                         (self.target_endpoint, application_guid))

    def get_env(self, application_guid):
        return super(ApplicationsManager, self)._get_one('%s/v2/apps/%s/env' %
                                                         (self.target_endpoint, application_guid))

    def start(self, application_guid, async=False, check_time=0.5):
        result = self.credentials_manager.put('%s/v2/apps/%s?stage_async=%s' %
                                              (self.target_endpoint, application_guid, json.dumps(async)),
                                              json=dict(state='STARTED'))
        if not async:
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

    def stop(self, application_guid, async=False, check_time=0.5):
        result = self.credentials_manager.put('%s/v2/apps/%s?stage_async=%s' %
                                              (self.target_endpoint, application_guid, json.dumps(async)),
                                              json=dict(state='STOPPED'))
        if not async:
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



