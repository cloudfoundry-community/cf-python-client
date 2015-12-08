#!/usr/bin/python2.7
import argparse
import sys
import os
import logging
import json
from cloudfoundry_client.client import CloudFoundryClient


__all__ = ['main', 'build_client_from_configuration']

_logger = logging.getLogger(__name__)


def _read_value_from_user(prompt, error_message=None, validator=None, default=''):
    while True:
        sys.stdout.write('%s : ' % prompt)
        sys.stdout.flush()
        answer_value = sys.stdin.readline().rstrip(' \r\n')
        if len(answer_value) == 0:
            answer_value = default
        if len(answer_value) > 0 and (validator is None or validator(answer_value)):
            return answer_value
        else:
            if error_message is None:
                sys.stderr.write('\"%s\": invalid value\n' % answer_value)
            else:
                sys.stderr.write('\"%s\": %s\n' % (answer_value, error_message))


def build_client_from_configuration():
    dir_conf = os.path.join(os.path.expanduser('~'))
    if not os.path.isdir(dir_conf):
        if os.path.exists(dir_conf):
            raise IOError('%s exists but is not a directory')
        os.mkdir(dir_conf)
    config_file = os.path.join(dir_conf, '.cf_client_python.json')
    if not os.path.isfile(config_file):
        target_endpoint = _read_value_from_user('Please enter a target endpoint',
                                                'Url must starts with http:// or https://',
                                                lambda s: s.startswith('http://') or s.startswith('https://'))
        skip_ssl_verification = _read_value_from_user('Skip ssl verification (true/false) [false]',
                                                      'Enter either true or false',
                                                      lambda s: s == 'true' or s == 'false', 'false')
        login = _read_value_from_user('Please enter your login')
        password = _read_value_from_user('Please enter your password')
        client = CloudFoundryClient(target_endpoint, skip_verification=(skip_ssl_verification == 'true'))
        client.credentials_manager.init_with_credentials(login, password)
        with open(config_file, 'w') as f:
            f.write(json.dumps(dict(target_endpoint=target_endpoint,
                                    skip_ssl_verification=(skip_ssl_verification == 'true'),
                                    access_token=client.credentials_manager.access_token(),
                                    refresh_token=client.credentials_manager.refresh_token()), indent=2))
        return client
    else:
        try:
            with open(config_file, 'r') as f:

                configuration = json.load(f)
                client = CloudFoundryClient(configuration['target_endpoint'],
                                            skip_verification=configuration['skip_ssl_verification'])
                client.credentials_manager.init_with_tokens(configuration['access_token'],
                                                            configuration['refresh_token'])
                return client
        except:
            sys.stderr.write('Could not restore configuration. Cleaning and recreating\n')
            os.remove(config_file)
            build_client_from_configuration()


def organizations(client, arguments):
    for organization in client.organization.list():
        _logger.info('%s - %s', organization['metadata']['guid'], organization['entity']['name'])


def spaces(client, arguments):
    def list_space(org_guid):
        for space in client.space.list(organization_guid=org_guid):
            _logger.info('%s - %s', space['metadata']['guid'], space['entity']['name'])

    if len(arguments.organization_id) > 0:
        list_space(arguments.organization_id)
    else:
        for organization in client.organization.list():
            _logger.info('Organization - %s - %s', organization['metadata']['guid'], organization['entity']['name'])
            list_space(organization['metadata']['guid'])


def applications(client, arguments):
    def list_app_of_space(space_guid):
        for app in client.application.list(space_guid=space_guid):
            _logger.info('      - %s - %s', app['metadata']['guid'], app['entity']['name'])

    def list_app_of_org(org_guid):
        for space in client.space.list(organization_guid=org_guid):
            _logger.info('  Space - %s - %s', space['metadata']['guid'], space['entity']['name'])
            list_app_of_space(space['metadata']['guid'])

    if len(arguments.space_id) > 0:
        list_app_of_space(arguments.space_id)
    elif len(arguments.organization_id) > 0:
        list_app_of_org(arguments.organization_id)
    else:
        for organization in client.organization.list():
            _logger.info('Organization - %s - %s', organization['metadata']['guid'], organization['entity']['name'])
            list_app_of_org(organization['metadata']['guid'])


def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(message)s')
    client = build_client_from_configuration()
    parser = argparse.ArgumentParser(add_help=True);
    subparsers = parser.add_subparsers(help='commands', dest='action')
    subparsers.add_parser('organizations', help='List organizations')
    spaces_parser = subparsers.add_parser('spaces', help='List spaces')
    spaces_parser.add_argument('-organization_id', action='store', dest='organization_id', type=str, default='',
                               help='Organization id')
    apps_parser = subparsers.add_parser('applications', help='List applications')
    apps_parser.add_argument('-organization_id', action='store', dest='organization_id', type=str, default='',
                             help='Organization id')
    apps_parser.add_argument('-space_id', action='store', dest='space_id', type=str, default='',
                             help='Space id')
    arguments = parser.parse_args()
    globals()[arguments.action](client, arguments)


if __name__ == "__main__":
    main()