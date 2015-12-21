#!/usr/bin/python2.7
import argparse
import sys
import os
import logging
import json
import re
from cloudfoundry_client.calls import ConnectionError
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
        except Exception, ex:
            if type(ex) == ConnectionError:
                raise
            else:
                sys.stderr.write('Could not restore configuration. Cleaning and recreating\n')
                os.remove(config_file)
                build_client_from_configuration()


def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(message)s')
    client = build_client_from_configuration()
    parser = argparse.ArgumentParser(add_help=True)
    subparsers = parser.add_subparsers(help='commands', dest='action')
    commands = dict()
    commands['organization'] = dict(list=(), name='name', allow_retrieve_by_name=True)
    commands['space'] = dict(list=('organization_guid',), name='name', allow_retrieve_by_name=True)
    commands['application'] = dict(list=('organization_guid', 'space_guid',), name='name', allow_retrieve_by_name=True)
    commands['service'] = dict(list=(), name='label', allow_retrieve_by_name=True)
    commands['service_plan'] = dict(list=('service_guid', 'service_instance_guid'), name='name',
                                    allow_retrieve_by_name=False)
    commands['service_instance'] = dict(list=('organization_guid', 'space_guid', 'service_plan_guid'), name='name',
                                        allow_retrieve_by_name=False)
    commands['service_binding'] = dict(list=('app_guid', 'service_instance_guid'), name=None,
                                       allow_retrieve_by_name=False)

    for domain, command_description in commands.items():
        list_parser = subparsers.add_parser('list_%ss' % domain, help='List %ss' % domain)
        for filter_parameter in command_description['list']:
            list_parser.add_argument('-%s' % filter_parameter, action='store', dest=filter_parameter, type=str,
                                     default=None, help='Filter with %s' % filter_parameter)
        get_parser = subparsers.add_parser('get_%s' % domain, help='Get a %s' % domain)
        get_parser.add_argument('id', metavar='ids', type=str, nargs=1,
                                help='The id. Can be UUID or name (first found then)'
                                if command_description['allow_retrieve_by_name'] else 'The id (UUID)')

    arguments = parser.parse_args()
    if arguments.action.find('list_') == 0:
        domain = arguments.action[len('list_'): len(arguments.action) - 1]
        filter_list = dict()
        for filter_parameter in commands[domain]['list']:
            filter_value = getattr(arguments, filter_parameter)
            if filter_value is not None:
                filter_list[filter_parameter] = filter_value
        for entity in getattr(client, domain).list(**filter_list):
            name_property = commands[domain]['name']
            if name_property is not None:
                print('%s - %s' % (entity['metadata']['guid'], entity['entity'][name_property]))
            else:
                print(entity['metadata']['guid'])
    elif arguments.action.find('get_') == 0:
        domain = arguments.action[len('get_'):]
        if not(commands[domain]['allow_retrieve_by_name'])\
                or re.match('[\d|a-z]{8}-[\d|a-z]{4}-[\d|a-z]{4}-[\d|a-z]{4}-[\d|a-z]{12}', arguments.id[0].lower()) \
                is not None:
            print(json.dumps(getattr(client, domain).get(arguments.id[0]), indent=1))
        else:
            filter_get = dict()
            filter_get[commands[domain]['name']] = arguments.id[0]
            print(json.dumps(getattr(client, domain).get_first(**filter_get), indent=1))


if __name__ == "__main__":
    main()