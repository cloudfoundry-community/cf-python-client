import logging
import json

from cloudfoundry.calls import caller
from cloudfoundry.credentials import CredentialsManager
from organizations import OrganizationManager
from spaces import SpaceManager
from services import ServiceManager
from applications import ApplicationsManager

_logger = logging.getLogger(__name__)


class InvalidStatusCode(Exception):
    def __init__(self, status_code):
        self.status_code = status_code


class CloudFoundryClient(object):
    proxy = None

    def __init__(self, target_endpoint, client_id='cf', client_secret='', proxy=None, skip_verification=False):
        caller.proxy(proxy)
        caller.skip_verifications(skip_verification)
        self.target_endpoint = target_endpoint
        self.info = caller.get('%s/v2/info' % self.target_endpoint).json()
        self.credentials_manager = CredentialsManager(self.info, client_id, client_secret)
        self.organization = OrganizationManager(self.target_endpoint, self.credentials_manager)
        self.space = SpaceManager(self.target_endpoint, self.credentials_manager)
        self.services = ServiceManager(self.target_endpoint, self.credentials_manager)
        self.applications = ApplicationsManager(self.target_endpoint, self.credentials_manager)

    def init_with_credentials(self, login, password):
        self.credentials_manager.init_with_credentials(login, password)

    def init_with_refresh(self, refresh_token):
        self.credentials_manager.init_with_refresh(refresh_token)



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)5s - %(name)s -  %(message)s')
    _logger = logging.getLogger(__name__)
    _logger.debug('building client')
    client = CloudFoundryClient('https://api.nd-cfapi.itn.ftgroup', skip_verification=True)
    _logger.debug('info %s' % json.dumps(client.info))
    client.init_with_credentials('buce8373', 'ben666')
    searched_app_name = 'static_test'
    matched_org, matched_space, matched_app = None, None, None
    for organization in client.organization.list():
        _logger.debug('organization - %s - %s' % (organization['metadata']['guid'], organization['entity']['name']))
        for space in client.space.list(organization):
            _logger.debug('     space - %s - %s' % (space['metadata']['guid'], space['entity']['name']))
            for application in client.applications.list(space):
                _logger.debug('         application - %s - %s' % (application['metadata']['guid'],
                                                                  application['entity']['name']))
                if application['entity']['name'] == searched_app_name:
                    matched_org, matched_space, matched_app = organization, space, application
    if matched_app is not None:
        _logger.debug(json.dumps(matched_app))
        _logger.debug(json.dumps([
            instance['entity']['name'] for instance in client.services.list_instances(matched_space)
        ]))
        _logger.debug(json.dumps(client.applications.start(matched_app)))