from argparse import _SubParsersAction, Namespace
from typing import Callable

from cloudfoundry_client.client import CloudFoundryClient
from cloudfoundry_client.main.command_domain import CommandDomain, Command


class AppCommandDomain(CommandDomain):
    def __init__(self):
        super(AppCommandDomain, self).__init__(
            display_name="Applications",
            entity_name="app",
            filter_list_parameters=["organization_guid", "space_guid"],
            allow_retrieve_by_name=True,
            allow_deletion=True,
            extra_methods=[
                (
                    self.recent_logs(),
                    "Recent Logs",
                ),
                (
                    self.stream_logs(),
                    "Stream Logs",
                ),
                (self.simple_extra_command("env"), "Get the environment of an application"),
                (
                    self.simple_extra_command("instances"),
                    "Get the instances of an application",
                ),
                (
                    self.simple_extra_command("stats"),
                    "Get the stats of an application",
                ),
                (
                    self.simple_extra_command("summary"),
                    "Get the summary of an application",
                ),
                (
                    self.simple_extra_command("start"),
                    "Start an application",
                ),
                (
                    self.simple_extra_command("stop"),
                    "Stop an application",
                ),
                (
                    self.simple_extra_command("restage"),
                    "Restage an application",
                ),
                (self.app_routes(), "List the routes(host) of an application"),
                (self.restart_instance(), "Restart the instance of an application"),
            ],
        )

    def recent_logs(self) -> Command:
        def execute(client, arguments):
            resource_id = self.resolve_id(arguments.id[0], lambda x: self._get_client_domain(client).get_first(name=x))
            for envelope in client.doppler.recent_logs(resource_id):
                print(envelope)

        return Command("recent_logs", self._generate_id_command_parser("recent_logs"), execute)

    def stream_logs(self) -> Command:
        def execute(client, arguments):
            resource_id = self.resolve_id(arguments.id[0], lambda x: self._get_client_domain(client).get_first(name=x))
            try:
                for envelope in client.doppler.stream_logs(resource_id):
                    print(envelope)
            except KeyboardInterrupt:
                pass

        return Command("stream_logs", self._generate_id_command_parser("stream_logs"), execute)

    def simple_extra_command(self, entry) -> Command:
        def execute(client, arguments):
            resource_id = self.resolve_id(arguments.id[0], lambda x: self._get_client_domain(client).get_first(name=x))
            print(getattr(self._get_client_domain(client), entry)(resource_id).json(indent=1))

        return Command(entry, self._generate_id_command_parser(entry), execute)

    def app_routes(self) -> Command:
        def execute(client: CloudFoundryClient, arguments: Namespace):
            resource_id = self.resolve_id(arguments.id[0], lambda x: self._get_client_domain(client).get_first(name=x))
            for entity in getattr(self._get_client_domain(client), "list_routes")(resource_id):
                print("%s - %s" % (entity["metadata"]["guid"], entity["entity"]["host"]))

        return Command("app_routes", self._generate_id_command_parser("app_routes"), execute)

    def restart_instance(self) -> Command:
        def generate_parser(parser: _SubParsersAction):
            command_parser = parser.add_parser("restart_instance")
            command_parser.add_argument(
                "id", metavar="ids", type=str, nargs=1, help="The id. Can be UUID or name (first found then)"
            )
            command_parser.add_argument("instance_id", metavar="instance_ids", type=int, nargs=1, help="The instance id")

        def execute(client: CloudFoundryClient, arguments: Namespace):
            app_domain = self._get_client_domain(client)
            resource_id = self.resolve_id(arguments.id[0], lambda x: app_domain.get_first(name=x))
            getattr(app_domain, "restart_instance")(resource_id, int(arguments.instance_id[0]))

        return Command("restart_instance", generate_parser, execute)

    @staticmethod
    def _generate_id_command_parser(entry: str) -> Callable[[_SubParsersAction], None]:
        def generate_parser(parser: _SubParsersAction):
            command_parser = parser.add_parser(entry)
            command_parser.add_argument(
                "id", metavar="ids", type=str, nargs=1, help="The id. Can be UUID or name (first found then)"
            )

        return generate_parser
