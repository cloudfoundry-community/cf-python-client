#!/usr/bin/python2.7
import argparse
import httplib
import logging
import os
import re
import sys
import json

from requests.exceptions import ConnectionError

from cloudfoundry_client.client import CloudFoundryClient
from cloudfoundry_client.entities import InvalidStatusCode

__all__ = ['main', 'build_client_from_configuration']

_logger = logging.getLogger(__name__)


def _read_value_from_user(prompt, error_message=None, validator=None, default=''):
    while True:
        sys.stdout.write('%s [%s]: ' % (prompt, default))
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


def build_client_from_configuration(previous_configuration=None):
    dir_conf = os.path.join(os.path.expanduser('~'))
    if not os.path.isdir(dir_conf):
        if os.path.exists(dir_conf):
            raise IOError('%s exists but is not a directory')
        os.mkdir(dir_conf)
    config_file = os.path.join(dir_conf, '.cf_client_python.json')
    if not os.path.isfile(config_file):
        target_endpoint = _read_value_from_user('Please enter a target endpoint',
                                                'Url must starts with http:// or https://',
                                                lambda s: s.startswith('http://') or s.startswith('https://'),
                                                default='' if previous_configuration is None else
                                                previous_configuration.get('target_endpoint', ''))
        skip_ssl_verification = _read_value_from_user('Skip ssl verification (true/false)',
                                                      'Enter either true or false',
                                                      lambda s: s == 'true' or s == 'false',
                                                      default='false' if previous_configuration is None else
                                                      json.dumps(
                                                          previous_configuration.get('skip_ssl_verification', False)))
        login = _read_value_from_user('Please enter your login')
        password = _read_value_from_user('Please enter your password')
        client = CloudFoundryClient(target_endpoint, skip_verification=(skip_ssl_verification == 'true'))
        client.init_with_user_credentials(login, password)
        with open(config_file, 'w') as f:
            f.write(json.dumps(dict(target_endpoint=target_endpoint,
                                    skip_ssl_verification=(skip_ssl_verification == 'true'),
                                    refresh_token=client.refresh_token), indent=2))
        return client
    else:
        try:
            configuration = None
            with open(config_file, 'r') as f:
                configuration = json.load(f)
                client = CloudFoundryClient(configuration['target_endpoint'],
                                            skip_verification=configuration['skip_ssl_verification'])
                client.init_with_token(configuration['refresh_token'])
                return client
        except Exception, ex:
            if type(ex) == ConnectionError:
                raise
            else:
                _logger.exception("Could not restore configuration. Cleaning and recreating")
                os.remove(config_file)
                return build_client_from_configuration(configuration)


def is_guid(s):
    return re.match(r'[\d|a-z]{8}-[\d|a-z]{4}-[\d|a-z]{4}-[\d|a-z]{4}-[\d|a-z]{12}', s.lower()) is not None


def resolve_id(argument, get_by_name, domain_name, allow_search_by_name):
    if is_guid(argument):
        return argument
    elif allow_search_by_name:
        result = get_by_name(argument)
        if result is not None:
            return result['metadata']['guid']
        else:
            raise InvalidStatusCode(httplib.NOT_FOUND, '%s with name %s' % (domain_name, argument))
    else:
        raise ValueError('id: %s: does not allow search by name' % domain_name)


def log_recent(client, application_guid):
    for message in client.loggregator.get_recent(application_guid):
        _logger.info(message.message)


def _get_client_domain(client, domain):
    return getattr(client, '%ss' % domain)


def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(message)s')
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    commands = dict()
    commands['organization'] = dict(list=(), name='name', allow_retrieve_by_name=True, allow_creation=True,
                                    allow_deletion=True, display_name='Organizations')
    commands['space'] = dict(list=('organization_guid',), name='name', allow_retrieve_by_name=True, allow_creation=True,
                             allow_deletion=True, display_name='Spaces')
    commands['app'] = dict(list=('organization_guid', 'space_guid',), name='name',
                           allow_retrieve_by_name=True, allow_creation=True, allow_deletion=True,
                           display_name='Applications')
    commands['service'] = dict(list=('service_broker_guid',), name='label', allow_retrieve_by_name=True,
                               allow_creation=True,
                               allow_deletion=True, display_name='Services')
    commands['service_plan'] = dict(list=('service_guid', 'service_instance_guid', 'service_broker_guid'), name='name',
                                    allow_retrieve_by_name=False, allow_creation=False, allow_deletion=False,
                                    display_name='Service plans')
    commands['service_instance'] = dict(list=('organization_guid', 'space_guid', 'service_plan_guid'), name='name',
                                        allow_retrieve_by_name=False, allow_creation=True, allow_deletion=True,
                                        display_name='Service instances')
    commands['service_binding'] = dict(list=('app_guid', 'service_instance_guid'), name=None,
                                       allow_retrieve_by_name=False, allow_creation=True, allow_deletion=True,
                                       display_name='Service bindings')
    commands['service_broker'] = dict(list=('name', 'space_guid'), name='name',
                                      allow_retrieve_by_name=True, allow_creation=True, allow_deletion=True,
                                      display_name='Service brokers')
    commands['buildpack'] = dict(list=(), name='name',
                                 allow_retrieve_by_name=False, allow_creation=False, allow_deletion=False,
                                 display_name='Buildpacks')
    commands['route'] = dict(list=(), name='host',
                             allow_retrieve_by_name=False, allow_creation=False, allow_deletion=False,
                             display_name='Routes')
    application_commands = dict(recent_logs=('get_recent_logs', 'Recent Logs',),
                                env=('get_env', 'Get the environment of an application',),
                                instances=('get_instances', 'Get the instances of an application',),
                                stats=('get_stats', 'Get the stats of an application',),
                                summary=('get_summary', 'Get the summary of an application',),
                                start=('start', 'Start an application',),
                                stop=('stop', 'Stop an application',))
    application_extra_list_commands = dict(routes=('list_routes', 'List the routes(host) of an application', 'host'))
    description = []
    for domain, command_description in commands.items():
        description.append(' %s' % command_description['display_name'])
        description.append('   list_%ss : List %ss' % (domain, domain))
        description.append('   get_%s : Get a %s by %s' % (domain, domain,
                                                           'UUID or name (first found then)'
                                                           if command_description['allow_retrieve_by_name']
                                                           else 'UUID'))
        if command_description['allow_creation']:
            description.append('   create_%s : Create a %s' % (domain, domain))
        if command_description['allow_deletion']:
            description.append('   delete_%s : Delete a %s' % (domain, domain))
        if domain == 'application':
            for command, application_command_description in application_commands.items():
                description.append('   %s : %s' % (command, application_command_description[1]))
            for command, application_command_description in application_extra_list_commands.items():
                description.append('   %s : %s' % (command, application_command_description[1]))
        description.append('')

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(title='Commands', dest='action', description='\n'.join(description))
    for domain, command_description in commands.items():
        list_parser = subparsers.add_parser('list_%ss' % domain)
        for filter_parameter in command_description['list']:
            list_parser.add_argument('-%s' % filter_parameter, action='store', dest=filter_parameter, type=str,
                                     default=None, help='Filter with %s' % filter_parameter)
        get_parser = subparsers.add_parser('get_%s' % domain)
        get_parser.add_argument('id', metavar='ids', type=str, nargs=1,
                                help='The id. Can be UUID or name (first found then)'
                                if command_description['allow_retrieve_by_name'] else 'The id (UUID)')
        if command_description['allow_creation']:
            create_parser = subparsers.add_parser('create_%s' % domain)
            create_parser.add_argument('entity', metavar='entities', type=str, nargs=1,
                                       help='Either a path of the json file containing the %s or a json object' % domain)
        if command_description['allow_deletion']:
            delete_parser = subparsers.add_parser('delete_%s' % domain)
            delete_parser.add_argument('id', metavar='ids', type=str, nargs=1,
                                       help='The id. Can be UUID or name (first found then)'
                                       if command_description['allow_retrieve_by_name'] else 'The id (UUID)')
        if domain == 'app':
            for command, application_command_description in application_commands.items():
                command_parser = subparsers.add_parser(command)
                command_parser.add_argument('id', metavar='ids', type=str, nargs=1,
                                            help='The id. Can be UUID or name (first found then)')
            for command, application_command_description in application_extra_list_commands.items():
                command_parser = subparsers.add_parser(command)
                command_parser.add_argument('id', metavar='ids', type=str, nargs=1,
                                            help='The id. Can be UUID or name (first found then)')

    arguments = parser.parse_args()
    client = build_client_from_configuration()
    if arguments.action == 'recent_logs':
        resource_id = resolve_id(arguments.id[0], lambda x: client.apps.get_first(name=x), 'application', True)
        log_recent(client, resource_id)
    elif application_commands.get(arguments.action) is not None:
        resource_id = resolve_id(arguments.id[0], lambda x: client.apps.get_first(name=x), 'application', True)
        print(getattr(client.apps, application_commands[arguments.action][0])(resource_id).json(indent=1))
    elif application_extra_list_commands.get(arguments.action) is not None:
        resource_id = resolve_id(arguments.id[0], lambda x: client.apps.get_first(name=x), 'application', True)
        name_property = application_extra_list_commands[arguments.action][2]
        for entity in getattr(client.apps, application_extra_list_commands[arguments.action][0])(resource_id):
            print('%s - %s' % (entity['metadata']['guid'], entity['entity'][name_property]))
    elif arguments.action.find('list_') == 0:
        domain = arguments.action[len('list_'): len(arguments.action) - 1]
        filter_list = dict()
        for filter_parameter in commands[domain]['list']:
            filter_value = getattr(arguments, filter_parameter)
            if filter_value is not None:
                filter_list[filter_parameter] = filter_value
        for entity in _get_client_domain(client, domain).list(**filter_list):
            name_property = commands[domain]['name']
            if name_property is not None:
                print('%s - %s' % (entity['metadata']['guid'], entity['entity'][name_property]))
            else:
                print(entity['metadata']['guid'])
    elif arguments.action.find('get_') == 0:
        domain = arguments.action[len('get_'):]
        resource_id = resolve_id(arguments.id[0],
                                 lambda x: _get_client_domain(client, domain).get_first(
                                     **{commands[domain]['name']: x}),
                                 domain,
                                 commands[domain]['allow_retrieve_by_name'])
        print(_get_client_domain(client, domain).get(resource_id).json(indent=1))
    elif arguments.action.find('create_') == 0:
        domain = arguments.action[len('create_'):]
        data = None
        if os.path.isfile(arguments.entity[0]):
            with open(arguments.entity[0], 'r') as f:
                try:
                    data = json.load(f)
                except ValueError, _:
                    raise ValueError('entity: file %s does not contain valid json data' % arguments.entity[0])
        else:
            try:
                data = json.loads(arguments.entity[0])
            except ValueError:
                raise ValueError('entity: must be either a valid json file path or a json object')
        print(_get_client_domain(client, domain)._create(data.json()))
    elif arguments.action.find('delete_') == 0:
        domain = arguments.action[len('delete_'):]
        if is_guid(arguments.id[0]):
            _get_client_domain(client, domain)._remove(arguments.id[0])
        elif commands[domain]['allow_retrieve_by_name']:
            filter_get = dict()
            filter_get[commands[domain]['name']] = arguments.id[0]
            entity = _get_client_domain(client, domain).get_first(**filter_get)
            if entity is None:
                raise InvalidStatusCode(httplib.NOT_FOUND, '%s with name %s' % (domain, arguments.id[0]))
            else:
                _get_client_domain(client, domain)._remove(entity['metadata']['guid'])
        else:
            raise ValueError('id: %s: does not allow search by name' % domain)


if __name__ == "__main__":
    main()
