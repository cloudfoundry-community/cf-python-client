import json
import os
from argparse import Namespace, _SubParsersAction

from cloudfoundry_client.client import CloudFoundryClient
from cloudfoundry_client.json_object import JsonObject
from cloudfoundry_client.main.command_domain import CommandDomain, Command


class TaskCommandDomain(CommandDomain):
    def __init__(self):
        super(TaskCommandDomain, self).__init__(
            display_name="Tasks",
            entity_name="task",
            filter_list_parameters=["names", "app_guids", "space_guids", "organization_guids"],
            api_version="v3",
            allow_creation=True,
            allow_deletion=False,
            extra_methods=[
                (
                    self.cancel(),
                    "Cancel Task",
                )
            ],
        )

    def id(self, entity: JsonObject) -> str:
        return entity["guid"]

    def name(self, entity: JsonObject) -> str:
        return entity[self.name_property]

    def find_by_name(self, client: CloudFoundryClient, name: str):
        return self._get_client_domain(client).get_first(**{"%ss" % self.name_property: name})

    def create(self) -> Command:
        entry = self._create_entry()

        def execute(client: CloudFoundryClient, arguments: Namespace):
            data = None
            if os.path.isfile(arguments.entity[0]):
                with open(arguments.entity[0], "r") as f:
                    try:
                        data = json.load(f)
                    except ValueError:
                        raise ValueError("entity: file %s does not contain valid json data" % arguments.entity[0])
            else:
                try:
                    data = json.loads(arguments.entity[0])
                except ValueError:
                    raise ValueError("entity: must be either a valid json file path or a json object")
            print(self._get_client_domain(client).create(arguments.app_id[0], **data).json())

        def generate_parser(parser: _SubParsersAction):
            create_parser = parser.add_parser(entry)
            create_parser.add_argument("app_id", metavar="ids", type=str, nargs=1, help="The application UUID.")
            create_parser.add_argument(
                "entity",
                metavar="entities",
                type=str,
                nargs=1,
                help="Either a path of the json file containing the %s or a json object or the json %s object"
                % (self.client_domain, self.client_domain),
            )

        return Command(entry, generate_parser, execute)

    def cancel(self) -> Command:
        entry = "cancel_task"

        def execute(client: CloudFoundryClient, arguments: Namespace):
            print(self._get_client_domain(client).cancel(arguments.id[0]).json(indent=1))

        def generate_parser(parser: _SubParsersAction):
            command_parser = parser.add_parser(entry)
            command_parser.add_argument("id", metavar="ids", type=str, nargs=1, help="The task UUID")

        return Command(entry, generate_parser, execute)
