import logging
import requests
import json
import base64

_logger = logging.getLogger(__name__)


class CloudFoundryClient(object):
    proxy = None

    def __init__(self, target_endpoint, client_id='cf', client_secret='', skip_verification=False):
        self.target_endpoint = target_endpoint
        self.client_id = client_id
        self.client_secret = client_secret
        self.skip_verification = skip_verification
        self.info = self._get_info()
        self.credentials = None

    def _get_info(self):
        response = requests.get('%s/v2/info' % self.target_endpoint,
                                proxies=CloudFoundryClient.proxy,
                                verify=not self.skip_verification)
        return response.json()

    def init_credentials(self, login, password):
        self._get_credentials(dict(grant_type='password', username=login, password=password))

    def refresh_token(self, refresh_token):
        self._get_credentials(dict(grant_type='refresh_token', scope='', refresh_token=refresh_token))

    def _get_credentials(self, data):
        response = requests.post('%s/oauth/token' % self.info['authorization_endpoint'],
                                 proxies=CloudFoundryClient.proxy,
                                 verify=not self.skip_verification,
                                 data=data,
                                 headers=dict(Authorization=
                                              'Basic %s' % base64.b64encode(
                                                  '%s:%s' % (self.client_id, self.client_secret))
                                              )
                                 )
        self.credentials = response.json()

    def list_organizations(self):
        return self._read_resource('/v2/organizations')

    def list_spaces(self, organization_entity):
        return self._read_resource(organization_entity['entity']['spaces_url'])

    def list_applications(self, space_entity):
        return self._read_resource(space_entity['entity']['apps_url'])

    def list_service_instances(self, space_entity):
        return self._read_resource(space_entity['entity']['service_instances_url'])

    def list_service_bindings(self, application_entity):
        return self._read_resource(application_entity['entity']['service_bindings_url'])

    def start_application(self, application, async=False):
        return self._change_application_state(application, 'STARTED', async)

    def stop_application(self, application, async=False):
        return self._change_application_state(application, 'STOPPED', async)

    def _change_application_state(self, application, state, async):
        response = requests.put('%s%s?stage_async=%s' %
                                (self.target_endpoint, application['metadata']['url'], json.dumps(async)),
                                json=dict(state=state),
                                proxies=CloudFoundryClient.proxy,
                                verify=not self.skip_verification,
                                headers=dict(Authorization='Bearer %s' % self.credentials['access_token'])
                                )
        return response.json()

    def _read_resource(self, url):
        response = requests.get('%s%s' % (self.target_endpoint, url),
                                proxies=CloudFoundryClient.proxy,
                                verify=not self.skip_verification,
                                headers=dict(Authorization='Bearer %s' % self.credentials['access_token'])
                                )
        return response.json()



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)5s - %(name)s -  %(message)s')
    _logger = logging.getLogger(__name__)
    _logger.debug('building client')
    client = CloudFoundryClient('https://api.nd-cfapi.itn.ftgroup', skip_verification=True)
    _logger.debug('info %s' % json.dumps(client.info))
    client.init_credentials('buce8373', 'ben666')
    _logger.debug('credentials %s' % json.dumps(client.credentials, indent=1))
    client.refresh_token(client.credentials['refresh_token'])
    _logger.debug('token refreshed %s' % json.dumps(client.credentials, indent=1))
    searched_app_name = 'static_test'
    matched_org, matched_space, matched_app = None, None, None
    for organization in client.list_organizations()['resources']:
        _logger.debug('organization - %s - %s' % (organization['metadata']['guid'], organization['entity']['name']))
        for space in client.list_spaces(organization)['resources']:
            _logger.debug('     space - %s - %s' % (space['metadata']['guid'], space['entity']['name']))
            for application in client.list_applications(space)['resources']:
                _logger.debug('         application - %s - %s' % (application['metadata']['guid'],
                                                              application['entity']['name']))
                if application['entity']['name'] == searched_app_name:
                    matched_org, matched_space, matched_app = organization, space, application
    if matched_app is not None:
        _logger.debug(json.dumps(matched_app))
        _logger.debug(json.dumps(client.list_service_instances(matched_space)))
        _logger.debug(json.dumps(client.start_application(matched_app)))