import logging
import re

_logger = logging.getLogger(__name__)


class LoggregatorManager(object):

    def __init__(self, logging_endpoint, credentials_manager):
        self.logging_endpoint = logging_endpoint
        self.credentials_manager = credentials_manager

    def get_recent(self, application_guid):
        url = '%s/recent?app=%s' % (re.sub(r'^ws', 'http', self.logging_endpoint), application_guid)
        return self.credentials_manager.get(url, False)