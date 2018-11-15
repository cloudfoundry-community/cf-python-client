import functools
import json
import os
import re
from collections import OrderedDict

from cloudfoundry_client.errors import InvalidStatusCode
from cloudfoundry_client.imported import NOT_FOUND


class Command(object):
    def __init__(self, entry, generate_parser, execute):
        self.entry = entry
        self.generate_parser = generate_parser
        self.execute = execute


class CommandDomain(object):
    def __init__(self, display_name, client_domain, filter_list_parameters,
                 api_version='v2', name_property='name',
                 allow_retrieve_by_name=False, allow_creation=False, allow_deletion=False,
                 extra_methods=None):
        self.display_name = display_name
        self.client_domain = client_domain
        self.api_version = api_version
        self.entity_name = client_domain[:len(client_domain) - 1]
        self.filter_list_parameters = filter_list_parameters
        self.name_property = name_property
        self.allow_retrieve_by_name = allow_retrieve_by_name
        self.allow_creation = allow_creation
        self.allow_deletion = allow_deletion

        self.commands = OrderedDict()
        self.commands[self._list_entry()] = self.list()
        self.commands[self._get_entry()] = self.get()
        if self.allow_creation:
            self.commands[self._create_entry()] = self.create()
        if self.allow_deletion:
            self.commands[self._delete_entry()] = self.delete()
        self.extra_description = OrderedDict()
        if extra_methods is not None:
            for command in extra_methods:
                self.commands[command[0].entry] = command[0]
                self.extra_description[command[0].entry] = command[1]

    def description(self):
        description = [' %s' % self.display_name,
                       '   %s : List %ss' % (self._list_entry(), self.entity_name),
                       '   %s : Get a %s by %s' % (self._get_entry(), self.entity_name,
                                                   'UUID or name (first found then)'
                                                   if self.allow_retrieve_by_name
                                                   else 'UUID')]
        if self.allow_creation:
            description.append('   %s : Create a %s' % (self._create_entry(), self.entity_name))

        if self.allow_deletion:
            description.append('   %s : Delete a %s' % (self._delete_entry(), self.entity_name))
        description.extend(['   %s : %s' % (k, v) for k, v in self.extra_description.items()])
        return description

    def generate_parser(self, parser):
        for command in self.commands.values():
            command.generate_parser(parser)

    def is_handled(self, action):
        return action in self.commands

    def execute(self, client, action, arguments):
        return self.commands[action].execute(client, arguments)

    def _get_client_domain(self, client):
        return getattr(getattr(client, self.api_version), self.client_domain)

    @staticmethod
    def is_guid(s):
        return re.match(r'[\d|a-z]{8}-[\d|a-z]{4}-[\d|a-z]{4}-[\d|a-z]{4}-[\d|a-z]{12}', s.lower()) is not None

    def resolve_id(self, argument, get_by_name):
        if CommandDomain.is_guid(argument):
            return argument
        elif self.allow_retrieve_by_name:
            result = get_by_name(argument)
            if result is not None:
                return result['metadata']['guid']
            else:
                raise InvalidStatusCode(NOT_FOUND, '%s with name %s' % (self.client_domain, argument))
        else:
            raise ValueError('id: %s: does not allow search by name' % self.client_domain)

    @staticmethod
    def id(entity):
        return entity['metadata']['guid']

    def name(self, entity):
        return entity['entity'][self.name_property]

    def find_by_name(self, client, name):
        return self._get_client_domain(client).get_first(**{self.name_property: name})

    def create(self):
        entry = self._create_entry()

        def execute(client, arguments):
            data = None
            if os.path.isfile(arguments.entity[0]):
                with open(arguments.entity[0], 'r') as f:
                    try:
                        data = json.load(f)
                    except ValueError:
                        raise ValueError('entity: file %s does not contain valid json data' % arguments.entity[0])
            else:
                try:
                    data = json.loads(arguments.entity[0])
                except ValueError:
                    raise ValueError('entity: must be either a valid json file path or a json object')
            print(self._get_client_domain(client)._create(data).json())

        def generate_parser(parser):
            create_parser = parser.add_parser(entry)
            create_parser.add_argument('entity', metavar='entities', type=str, nargs=1,
                                       help='Either a path of the json file containing the %s or a json object or the json %s object' % (
                                           self.client_domain, self.client_domain))

        return Command(entry, generate_parser, execute)

    def delete(self):
        entry = self._delete_entry()

        def execute(client, arguments):
            if self.is_guid(arguments.id[0]):
                self._get_client_domain(client)._remove(arguments.id[0])
            elif self.allow_retrieve_by_name:
                entity = self.find_by_name(client, arguments.id[0])
                if entity is None:
                    raise InvalidStatusCode(NOT_FOUND, '%s with name %s' % (self.client_domain, arguments.id[0]))
                else:
                    self._get_client_domain(client)._remove(self.id(entity))
            else:
                raise ValueError('id: %s: does not allow search by name' % self.client_domain)

        def generate_parser(parser):
            delete_parser = parser.add_parser(entry)
            delete_parser.add_argument('id', metavar='ids', type=str, nargs=1,
                                       help='The id. Can be UUID or name (first found then)'
                                       if self.allow_retrieve_by_name else 'The id (UUID)')

        return Command(entry, generate_parser, execute)

    def get(self):
        entry = self._get_entry()

        def execute(client, arguments):
            resource_id = self.resolve_id(arguments.id[0],
                                          functools.partial(self.find_by_name, client))
            print(self._get_client_domain(client).get(resource_id).json(indent=1))

        def generate_parser(parser):
            get_parser = parser.add_parser(entry)
            get_parser.add_argument('id', metavar='ids', type=str, nargs=1,
                                    help='The id. Can be UUID or name (first found then)'
                                    if self.allow_retrieve_by_name else 'The id (UUID)')

        return Command(entry, generate_parser, execute)

    def list(self):
        entry = self._list_entry()

        def execute(client, arguments):
            filter_list = dict()
            for filter_parameter in self.filter_list_parameters:
                filter_value = getattr(arguments, filter_parameter)
                if filter_value is not None:
                    filter_list[filter_parameter] = filter_value
            for entity in self._get_client_domain(client).list(**filter_list):
                if self.name_property is not None:
                    print('%s - %s' % (self.id(entity), self.name(entity)))
                else:
                    print(self.id(entity))

        def generate_parser(parser):
            list_parser = parser.add_parser(entry)
            for filter_parameter in self.filter_list_parameters:
                list_parser.add_argument('-%s' % filter_parameter, action='store', dest=filter_parameter, type=str,
                                         default=None, help='Filter with %s' % filter_parameter)

        return Command(entry, generate_parser, execute)

    def _list_entry(self):
        return 'list_%ss' % self.entity_name

    def _create_entry(self):
        return 'create_%s' % self.entity_name

    def _delete_entry(self):
        return 'delete_%s' % self.entity_name

    def _get_entry(self):
        return 'get_%s' % self.entity_name
