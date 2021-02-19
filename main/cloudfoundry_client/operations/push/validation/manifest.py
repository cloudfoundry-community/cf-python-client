import json
import os
import re

import yaml


class ManifestReader(object):
    MEMORY_PATTERN = re.compile(r"^(\d+)([KMGT])B?$")

    POSITIVE_FIELDS = ["instances", "timeout"]

    BOOLEAN_FIELDS = ["no-route", "random-route"]

    @staticmethod
    def load_application_manifests(manifest_path: str):
        with open(manifest_path, "r") as fp:
            manifest = yaml.safe_load(fp)
            if manifest is None:
                raise AssertionError("No valid yaml document found")
            ManifestReader._validate_manifest(os.path.dirname(manifest_path), manifest)
            return manifest["applications"]

    @staticmethod
    def _validate_manifest(manifest_directory: str, manifest: dict):
        for app_manifest in manifest["applications"]:
            ManifestReader._validate_application_manifest(manifest_directory, app_manifest)

    @staticmethod
    def _validate_application_manifest(manifest_directory: str, app_manifest: dict):
        name = app_manifest.get("name")
        if name is None or len(name) == 0:
            raise AssertionError("name must be set")
        docker_manifest = app_manifest.get("docker")
        if docker_manifest is not None:
            if app_manifest.get("path") is not None:
                raise AssertionError("Both path and docker cannot be set")
            ManifestReader._validate_application_docker(docker_manifest)
        elif "path" not in app_manifest:
            raise AssertionError("One of path or docker must be set")
        else:
            ManifestReader._absolute_path(manifest_directory, app_manifest)
        ManifestReader._convert_memory(app_manifest)
        for field in ManifestReader.POSITIVE_FIELDS:
            ManifestReader._convert_positive(app_manifest, field)
        for field in ManifestReader.BOOLEAN_FIELDS:
            ManifestReader._convert_boolean(app_manifest, field)
        ManifestReader._convert_environment(app_manifest)
        ManifestReader._check_deprecated_attributes(app_manifest)
        ManifestReader._validate_routes(app_manifest)

    @staticmethod
    def _check_deprecated_attributes(app_manifest: dict):
        if (
            app_manifest.get("hosts") is not None
            or app_manifest.get("host")
            or app_manifest.get("domains") is not None
            or app_manifest.get("domain")
            or app_manifest.get("no-hostname") is not None
        ):
            raise AssertionError("hosts, host, domains, domain and no-hostname are all deprecated. Use the routes attribute")

    @staticmethod
    def _convert_memory(manifest: dict):
        if "memory" in manifest:
            memory = manifest["memory"].upper()
            match = ManifestReader.MEMORY_PATTERN.match(memory)
            if match is None:
                raise AssertionError("Invalid memory format: %s" % memory)

            memory_number = int(match.group(1))
            if match.group(2) == "K":
                memory_number *= 1024
            elif match.group(2) == "M":
                memory_number *= 1024 * 1024
            elif match.group(2) == "G":
                memory_number *= 1024 * 1024 * 1024
            elif match.group(2) == "T":
                memory_number *= 1024 * 1024 * 1024 * 1024
            else:
                raise AssertionError("Invalid memory unit: %s" % memory)
            manifest["memory"] = int(memory_number / (1024 * 1024))

    @staticmethod
    def _convert_positive(manifest: dict, field: str):
        if field in manifest:
            value = int(manifest[field])
            if value < 1:
                raise AssertionError("Invalid %s value: %s. It ust be positive" % (field, value))
            manifest[field] = value

    @staticmethod
    def _convert_boolean(manifest: dict, field: str):
        if field in manifest:
            field_value = manifest[field]
            manifest[field] = field_value if type(field_value) == bool else field_value.lower() == "true"

    @staticmethod
    def _validate_routes(manifest: dict):
        for route in manifest.get("routes", []):
            if type(route) != dict or "route" not in route:
                raise AssertionError("routes attribute must be a list of object containing a route attribute")

    @staticmethod
    def _validate_application_docker(docker_manifest: dict):
        docker_image = docker_manifest.get("image")
        if docker_image is not None and docker_manifest.get("buildpack") is not None:
            raise AssertionError("image and buildpack can not both be set for docker")
        docker_username = docker_manifest.get("username")
        docker_password = docker_manifest.get("password")
        if docker_username is not None and docker_password is None or docker_username is None and docker_password is not None:
            raise AssertionError("Docker username/password must be set together or both be unset")
        if docker_username is not None and docker_password is not None and docker_image is None:
            raise AssertionError("Docker image not set while docker username/password are set")

    @staticmethod
    def _absolute_path(manifest_directory: str, manifest: dict):
        if "path" in manifest:
            path = manifest["path"]
            if path == os.path.abspath(path):
                manifest["path"] = path
            elif manifest_directory == "" or manifest_directory == ".":
                manifest["path"] = os.path.abspath(path)
            else:
                manifest["path"] = os.path.abspath(os.path.join(manifest_directory, path))

    @staticmethod
    def _convert_environment(app_manifest: dict):
        environment = app_manifest.get("env", None)
        if environment is not None:
            if type(environment) != dict:
                raise AssertionError("'env' entry must be a dictionary")
            app_manifest["env"] = {
                key: json.dumps(value) for key, value in environment.items() if value is not None and type(value) != str
            }
            app_manifest["env"].update(
                {key: value for key, value in environment.items() if value is not None and type(value) == str}
            )
