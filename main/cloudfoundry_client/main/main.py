#!/usr/bin/env python3
import argparse
import json
import logging
import os
import re
import sys
from http import HTTPStatus
from typing import Tuple, Callable, Any

from requests.exceptions import ConnectionError

from cloudfoundry_client import __version__
from cloudfoundry_client.client import CloudFoundryClient
from cloudfoundry_client.errors import InvalidStatusCode
from cloudfoundry_client.json_object import JsonObject
from cloudfoundry_client.main.apps_command_domain import AppCommandDomain
from cloudfoundry_client.main.command_domain import CommandDomain, Command
from cloudfoundry_client.main.operation_commands import generate_push_command
from cloudfoundry_client.main.tasks_command_domain import TaskCommandDomain

__all__ = ["main", "build_client_from_configuration"]

_logger = logging.getLogger(__name__)


def _read_value_from_user(
    prompt: str, error_message: str = None, validator: Callable[[str], bool] = None, default: str = ""
) -> str:
    while True:
        sys.stdout.write("%s [%s]: " % (prompt, default))
        sys.stdout.flush()
        answer_value = sys.stdin.readline().rstrip(" \r\n")
        if len(answer_value) == 0:
            answer_value = default
        if len(answer_value) > 0 and (validator is None or validator(answer_value)):
            return answer_value
        else:
            if error_message is None:
                sys.stderr.write('"%s": invalid value\n' % answer_value)
            else:
                sys.stderr.write('"%s": %s\n' % (answer_value, error_message))


def get_user_directory() -> str:
    dir_conf = os.path.join(os.path.expanduser("~"))
    if not os.path.isdir(dir_conf):
        if os.path.exists(dir_conf):
            raise IOError("%s exists but is not a directory")
        os.mkdir(dir_conf)
    return dir_conf


def get_config_file() -> str:
    return os.path.join(get_user_directory(), ".cf_client_python.json")


def import_from_clf_cli():
    user_directory = get_user_directory()
    cf_cli_dir = os.path.join(user_directory, ".cf")
    if not os.path.isdir(cf_cli_dir):
        raise IOError("%s directory not found" % cf_cli_dir)
    config_file = os.path.join(cf_cli_dir, "config.json")
    if not os.path.isfile(config_file):
        raise IOError("%s not found" % config_file)
    with open(config_file, "r") as cf_cli_file:
        cf_cli_data = json.load(cf_cli_file)
        if cf_cli_data["RefreshToken"] is None or cf_cli_data["Target"] is None:
            raise IOError("Could not load informations from cf cli configuration")
        with open(get_config_file(), "w") as f:
            f.write(
                json.dumps(
                    dict(target_endpoint=cf_cli_data["Target"], verify=False, refresh_token=cf_cli_data["RefreshToken"]), indent=2
                )
            )


def build_client_from_configuration(previous_configuration: dict = None) -> CloudFoundryClient:
    config_file = get_config_file()
    if not os.path.isfile(config_file):
        target_endpoint = _read_value_from_user(
            "Please enter a target endpoint",
            "Url must starts with http:// or https://",
            lambda s: s.startswith("http://") or s.startswith("https://"),
            default="" if previous_configuration is None else previous_configuration.get("target_endpoint", ""),
        )
        verify = _read_value_from_user(
            "Verify ssl (true/false)",
            "Enter either true or false",
            lambda s: s == "true" or s == "false",
            default="true" if previous_configuration is None else json.dumps(previous_configuration.get("verify", True)),
        )
        login = _read_value_from_user("Please enter your login")
        password = _read_value_from_user("Please enter your password")
        client = CloudFoundryClient(target_endpoint, verify=(verify == "true"))
        client.init_with_user_credentials(login, password)
        with open(config_file, "w") as f:
            f.write(
                json.dumps(
                    dict(target_endpoint=target_endpoint, verify=(verify == "true"), refresh_token=client.refresh_token), indent=2
                )
            )
        return client
    else:
        try:
            configuration = None
            with open(config_file, "r") as f:
                configuration = json.load(f)
                client = CloudFoundryClient(configuration["target_endpoint"], verify=configuration["verify"])
                client.init_with_token(configuration["refresh_token"])
                return client
        except Exception as ex:
            if type(ex) == ConnectionError:
                raise
            else:
                _logger.exception("Could not restore configuration. Cleaning and recreating")
                os.remove(config_file)
                return build_client_from_configuration(configuration)


def is_guid(s: str) -> bool:
    return re.match(r"[\d|a-z]{8}-[\d|a-z]{4}-[\d|a-z]{4}-[\d|a-z]{4}-[\d|a-z]{12}", s.lower()) is not None


def resolve_id(argument: str, get_by_name: Callable[[str], JsonObject], domain_name: str, allow_search_by_name: bool) -> str:
    if is_guid(argument):
        return argument
    elif allow_search_by_name:
        result = get_by_name(argument)
        if result is not None:
            return result["metadata"]["guid"]
        else:
            raise InvalidStatusCode(HTTPStatus.NOT_FOUND, "%s with name %s" % (domain_name, argument))
    else:
        raise ValueError("id: %s: does not allow search by name" % domain_name)


def log_recent(client: CloudFoundryClient, application_guid: str):
    for envelope in client.doppler.recent_logs(application_guid):
        _logger.info(envelope)


def stream_logs(client: CloudFoundryClient, application_guid: str):
    try:
        for envelope in client.doppler.stream_logs(application_guid):
            _logger.info(envelope)
    except KeyboardInterrupt:
        pass


def _get_v2_client_domain(client: CloudFoundryClient, domain: str) -> Any:
    return getattr(client.v2, "%ss" % domain)


def generate_oauth_token_command() -> Tuple[Command, str]:
    entry = "oauth-token"

    def generate_parser(parser: argparse._SubParsersAction):
        parser.add_parser(entry)

    def execute(client: CloudFoundryClient, arguments: argparse.Namespace):
        token = client._access_token
        print(token if token is not None else "No token")

    return Command(entry, generate_parser, execute), "Display oauth token"


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    commands = [
        CommandDomain(
            display_name="Organizations",
            entity_name="organization",
            api_version="v3",
            filter_list_parameters=["names", "guids"],
            allow_retrieve_by_name=True,
            allow_creation=True,
            allow_deletion=True,
        ),
        CommandDomain(
            display_name="OrganizationQuotas",
            entity_name="organization_quota",
            api_version="v3",
            filter_list_parameters=["names", "guids", "organization_guids"],
            allow_retrieve_by_name=True,
            allow_creation=True,
            allow_deletion=True,
        ),
        CommandDomain(
            display_name="Spaces",
            entity_name="space",
            filter_list_parameters=["organization_guid"],
            allow_retrieve_by_name=True,
            allow_creation=True,
            allow_deletion=True,
        ),
        AppCommandDomain(),
        CommandDomain(
            display_name="Services",
            entity_name="service",
            filter_list_parameters=["service_broker_guid"],
            name_property="label",
            allow_retrieve_by_name=True,
            allow_creation=True,
            allow_deletion=True,
        ),
        CommandDomain(
            display_name="Service Plans",
            entity_name="service_plan",
            filter_list_parameters=["service_guid", "service_instance_guid", "service_broker_guid"],
        ),
        CommandDomain(
            display_name="Service Instances",
            entity_name="service_instance",
            filter_list_parameters=["organization_guid", "space_guid", "service_plan_guid"],
            allow_creation=True,
            allow_deletion=True,
        ),
        CommandDomain(
            display_name="Service Keys",
            entity_name="service_key",
            filter_list_parameters=["service_instance_guid"],
            allow_creation=True,
            allow_deletion=True,
        ),
        CommandDomain(
            display_name="Service Bindings",
            entity_name="service_binding",
            filter_list_parameters=["app_guid", "service_instance_guid"],
            name_property=None,
            allow_creation=True,
            allow_deletion=True,
        ),
        CommandDomain(
            display_name="Service Broker",
            entity_name="service_broker",
            filter_list_parameters=["name", "space_guid"],
            allow_retrieve_by_name=True,
            allow_creation=True,
            allow_deletion=True,
        ),
        CommandDomain(
            display_name="Service Plan Visibilities",
            entity_name="service_plan_visibility",
            filter_list_parameters=["organization_guid", "service_plan_guid"],
            name_property=None,
            allow_retrieve_by_name=False,
            allow_creation=True,
            allow_deletion=True,
        ),
        CommandDomain(
            display_name="Buildpacks",
            entity_name="buildpack",
            api_version="v3",
            filter_list_parameters=["names", "stacks"],
            allow_retrieve_by_name=True,
            allow_creation=True,
            allow_deletion=True,
        ),
        CommandDomain(
            display_name="Domains",
            entity_name="domain",
            api_version="v3",
            filter_list_parameters=[],
            allow_retrieve_by_name=True,
            allow_creation=True,
            allow_deletion=True,
        ),
        CommandDomain(display_name="Routes", entity_name="route", name_property="host", filter_list_parameters=[]),
        TaskCommandDomain(),
    ]
    operation_commands = [generate_push_command()]
    others_commands = [generate_oauth_token_command()]

    descriptions = []
    for command in commands:
        descriptions.extend(command.description())

    descriptions.append("Operations")
    for command, description in operation_commands:
        descriptions.append("   %s: %s" % (command.entry, description))

    descriptions.append("Others")
    for command, description in others_commands:
        descriptions.append("   %s: %s" % (command.entry, description))

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-V", "--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(title="Commands", dest="action", description="\n".join(descriptions))
    subparsers.add_parser("import_from_cf_cli", help="Copy CF CLI configuration into our configuration")

    for command in commands:
        command.generate_parser(subparsers)
    for other_command_domain in [operation_commands, others_commands]:
        for command, _ in other_command_domain:
            command.generate_parser(subparsers)

    arguments = parser.parse_args()
    if arguments.action == "import_from_cf_cli":
        import_from_clf_cli()
    else:
        client = build_client_from_configuration()
        for command in commands:
            if command.is_handled(arguments.action):
                command.execute(client, arguments.action, arguments)
                return
        for other_command_domain in [operation_commands, others_commands]:
            for command, _ in other_command_domain:
                if command.entry == arguments.action:
                    command.execute(client, arguments)
                    return

        raise ValueError("Domain not found for action %s" % arguments.action)


if __name__ == "__main__":
    main()
