from cloudfoundry_client.main.command_domain import CommandDomain, Command


class AppCommandDomain(CommandDomain):
    def __init__(self):
        super(AppCommandDomain, self).__init__(display_name='Applications',
                                               client_domain='apps',
                                               filter_list_parameters=['organization_guid', 'space_guid'],
                                               allow_retrieve_by_name=True,
                                               allow_deletion=True,
                                               extra_methods=[(self.recent_logs(), 'Recent Logs',),
                                                              (self.stream_logs(), 'Stream Logs',),
                                                              (self.simple_extra_command('env'),
                                                               'Get the environment of an application'),
                                                              (self.simple_extra_command('instances'),
                                                               'Get the instances of an application',),
                                                              (self.simple_extra_command('stats'),
                                                               'Get the stats of an application',),
                                                              (self.simple_extra_command('summary'),
                                                               'Get the summary of an application',),
                                                              (self.simple_extra_command('start'),
                                                               'Start an application',),
                                                              (self.simple_extra_command('stop'),
                                                               'Stop an application',),
                                                              (self.simple_extra_command('restage'),
                                                               'Restage an application',),
                                                              (self.app_routes(),
                                                               'List the routes(host) of an application')])

    def recent_logs(self):
        def execute(client, arguments):
            resource_id = self.resolve_id(arguments.id[0], lambda x: self._get_client_domain(client).get_first(name=x))
            for envelope in client.doppler.recent_logs(resource_id):
                print(envelope)

        return Command('recent_logs', self._generate_id_command_parser('recent_logs'), execute)

    def stream_logs(self):
        def execute(client, arguments):
            resource_id = self.resolve_id(arguments.id[0], lambda x: self._get_client_domain(client).get_first(name=x))
            try:
                for envelope in client.doppler.stream_logs(resource_id):
                    print(envelope)
            except KeyboardInterrupt:
                pass

        return Command('stream_logs', self._generate_id_command_parser('stream_logs'), execute)

    def simple_extra_command(self, entry):
        def execute(client, arguments):
            resource_id = self.resolve_id(arguments.id[0], lambda x: self._get_client_domain(client).get_first(name=x))
            print(getattr(self._get_client_domain(client), entry)(resource_id).json(indent=1))

        return Command(entry, self._generate_id_command_parser(entry), execute)

    def app_routes(self):
        def execute(client, arguments):
            resource_id = self.resolve_id(arguments.id[0], lambda x: self._get_client_domain(client).get_first(name=x))
            for entity in getattr(self._get_client_domain(client), 'list_routes')(resource_id):
                print('%s - %s' % (entity['metadata']['guid'], entity['entity']['host']))

        return Command('app_routes', self._generate_id_command_parser('app_routes'), execute)

    @staticmethod
    def _generate_id_command_parser(entry):
        def generate_parser(parser):
            command_parser = parser.add_parser(entry)
            command_parser.add_argument('id', metavar='ids', type=str, nargs=1,
                                        help='The id. Can be UUID or name (first found then)')

        return generate_parser
