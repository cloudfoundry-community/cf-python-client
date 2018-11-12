import json
import logging
import os
import re
import shutil
import tempfile
import time

from cloudfoundry_client.operations.push.file_helper import FileHelper
from cloudfoundry_client.operations.push.validation.manifest import ManifestReader

_logger = logging.getLogger(__name__)


class PushOperation(object):
    UPLOAD_TIMEOUT = 15 * 60

    SPLIT_ROUTE_PATTERN = re.compile('(?P<protocol>[a-z]+://)?(?P<domain>[^:/]+)(?P<port>:\d+)?(?P<path>/.*)?')

    def __init__(self, client):
        self.client = client

    def push(self, space_id, manifest_path, restart=True):
        app_manifests = ManifestReader.load_application_manifests(manifest_path)
        organization, space = self._retrieve_space_and_organization(space_id)

        for app_manifest in app_manifests:
            if 'path' in app_manifest or 'docker' in app_manifest:
                self._push_application(organization, space, app_manifest, restart)

    def _retrieve_space_and_organization(self, space_id):
        space = self.client.v2.spaces.get(space_id)
        organization = space.organization()
        return organization, space

    def _push_application(self, organization, space, app_manifest, restart):
        app = self._init_application(space, app_manifest)
        self._route_application(organization, space, app, app_manifest.get('no-route', False),
                                app_manifest.get('routes', []), app_manifest.get('random-route', False))
        if 'path' in app_manifest:
            self._upload_application(app, app_manifest['path'])
        self._bind_services(space, app, app_manifest.get('services', []))
        if restart:
            PushOperation._restart_application(app)

    def _init_application(self, space, app_manifest):
        app = self.client.v2.apps.get_first(name=app_manifest['name'], space_guid=space['metadata']['guid'])
        return self._update_application(app, app_manifest) if app is not None \
            else self._create_application(space, app_manifest)

    def _create_application(self, space, app_manifest):
        _logger.debug("Creating application %s", app_manifest['name'])
        request = self._build_request_from_manifest(app_manifest)
        request['space_guid'] = space['metadata']['guid']
        if request.get('health-check-type') == 'http' and request.get('health-check-http-endpoint') is None:
            request['health-check-http-endpoint'] = '/'
        return self.client.v2.apps.create(**request)

    def _update_application(self, app, app_manifest):
        _logger.debug("Uploading application %s", app['entity']['name'])
        request = self._build_request_from_manifest(app_manifest)
        request['environment_json'] = PushOperation._merge_environment(app, app_manifest)
        if request.get('health-check-type') == 'http' and request.get('health-check-http-endpoint') is None \
                and app['entity'].get('health_check_http_endpoint') is None:
            request['health-check-http-endpoint'] = '/'
        return self.client.v2.apps.update(app['metadata']['guid'], **request)

    def _build_request_from_manifest(self, app_manifest):
        request = dict()
        request.update(app_manifest)
        stack = self.client.v2.stacks.get_first(name=app_manifest['stack']) if 'stack' in app_manifest else None
        if stack is not None:
            request['stack_guid'] = stack['metadata']['guid']
        docker = request.pop('docker', None)
        if docker is not None and 'image' in docker:
            request['docker_image'] = docker['image']
            request['diego'] = True
            if 'username' in docker and 'password' in docker:
                request['docker_credentials'] = dict(username=docker['username'], password=docker['password'])
        return request

    @staticmethod
    def _merge_environment(app, app_manifest):
        environment = dict()
        if 'environment_json' in app['entity']:
            environment.update(app['entity']['environment_json'])
        if 'env' in app_manifest:
            environment.update(app_manifest['env'])
        return environment

    def _route_application(self, organization, space, app, no_route, routes, random_route):
        existing_routes = [route for route in app.routes()]
        if no_route:
            self._remove_all_routes(app, existing_routes)
        elif len(routes) == 0 and len(existing_routes) == 0:
            self._build_default_route(space, app, random_route)
        else:
            self._build_new_requested_routes(organization, space, app, existing_routes, routes)

    def _remove_all_routes(self, app, routes):
        for route in routes:
            self.client.v2.apps.remove_route(app['metadata']['guid'], route['metadata']['guid'])

    def _build_default_route(self, space, app, random_route):
        shared_domain = None
        for domain in self.client.v2.shared_domains.list():
            if not domain['entity']['internal']:
                shared_domain = domain
                break
        if shared_domain is None:
            raise AssertionError('No route specified and no no-route field or shared domain')
        if shared_domain['entity'].get('router_group_type') == 'tcp':
            route = self.client.v2.routes.create_tcp_route(shared_domain['metadata']['guid'],
                                                           space['metadata']['guid'])
        elif random_route:
            route = self.client.v2.routes.create_host_route(shared_domain['metadata']['guid'],
                                                            space['metadata']['guid'],
                                                            '%s-%d' % (app['entity']['name'], int(time.time())))
        else:
            route = self.client.v2.routes.create_host_route(shared_domain['metadata']['guid'],
                                                            space['metadata']['guid'],
                                                            app['entity']['name'])
        self.client.v2.apps.associate_route(app['metadata']['guid'], route['metadata']['guid'])

    def _build_new_requested_routes(self, organization, space, app, existing_routes, requested_routes):
        private_domains = {domain['entity']['name']: domain for domain in organization.private_domains()}
        shared_domains = {domain['entity']['name']: domain for domain in self.client.v2.shared_domains.list()}
        for requested_route in requested_routes:
            route, port, path = PushOperation._split_route(requested_route)
            if len(path) > 0 and port is not None:
                _logger.error("Neither path nor port provided for route", requested_route)
                raise AssertionError('Cannot set both port and path for route: %s' % requested_route)
            host, domain_name, domain = PushOperation._resolve_domain(route, private_domains, shared_domains)
            if port is not None and host is not None:
                _logger.error('Host provided in route %s for tcp domain %s', requested_route, domain_name)
                raise AssertionError(
                    'For route (%s) refers to domain %s that is a tcp one. It is hence routed by port and not by host'
                    % (requested_route, domain_name))
            route_to_map = None
            if port is not None and domain['entity'].get('router_group_type') != 'tcp':
                _logger.error('Port provided in route %s for non tcp domain %s', requested_route, domain_name)
                raise AssertionError('Cannot set port on route(%s) for non tcp domain' % requested_route)
            elif domain['entity'].get('router_group_type') == 'tcp' and port is None:
                _logger.error('No port provided in route %s for tcp domain %s', requested_route, domain_name)
                raise AssertionError('Please specify a port on route (%s) for tcp domain' % requested_route)
            elif domain['entity'].get('router_group_type') == 'tcp':
                if not any([route['entity']['domain_guid'] == domain['metadata']['guid']
                            and route['entity']['port'] == port] for route in existing_routes):
                    route_to_map = self._resolve_new_tcp_route(space, domain, port)
            else:
                if not any([route['entity']['domain_guid'] == domain['metadata']['guid']
                            and route['entity']['host'] == host] for route in existing_routes):
                    route_to_map = self._resolve_new_host_route(space, domain, host, path)
            if route_to_map is not None:
                _logger.debug('Associating route %s to application %s', requested_route, app['entity']['name'])
                self.client.v2.apps.associate_route(app['metadata']['guid'], route_to_map['metadata']['guid'])

    def _resolve_new_host_route(self, space, domain, host, path):
        existing_route = self.client.v2.routes.get_first(domain_guid=domain['metadata']['guid'], host=host, path=path)
        if existing_route is None:
            _logger.debug('Creating host route %s on domain %s and path %s', host, domain['entity']['name'], path)
            existing_route = self.client.v2.routes.create_host_route(domain['metadata']['guid'],
                                                                     space['metadata']['guid'],
                                                                     host,
                                                                     path)
        else:
            _logger.debug('Host route %s on domain %s and path %s already exists with guid %s',
                          host,
                          domain['entity']['name'],
                          path,
                          existing_route['metadata']['guid'])
        return existing_route

    def _resolve_new_tcp_route(self, space, domain, port):
        existing_route = self.client.v2.routes.get_first(domain_guid=domain['metadata']['guid'], port=port)
        if existing_route is None:
            _logger.debug('Creating tcp route %d on domain %s', port, domain['entity']['name'])
            existing_route = self.client.v2.routes.create_tcp_route(domain['metadata']['guid'],
                                                                    space['metadata']['guid'],
                                                                    port)
        else:
            _logger.debug('TCP route %d on domain %s already exists with guid %s',
                          port,
                          domain['entity']['name'],
                          existing_route['metadata']['guid'])
        return existing_route

    @staticmethod
    def _split_route(requested_route):
        route_splitted = PushOperation.SPLIT_ROUTE_PATTERN.match(requested_route['route'])
        if route_splitted is None:
            raise AssertionError('Invalid route: %s' % requested_route['route'])
        domain = route_splitted.group('domain')
        port = route_splitted.group('port')
        path = route_splitted.group('path')
        return domain, int(port[1:]) if port is not None else None, '' if path is None or path == '/' else path

    @staticmethod
    def _resolve_domain(route, private_domains, shared_domains):
        for domains in [private_domains, shared_domains]:
            if route in domains:
                return '', route, domains[route]
            else:
                idx = route.find('.')
                if 0 < idx < (len(route) - 2):
                    host = route[:idx]
                    domain = route[idx + 1:]
                    if domain in domains:
                        return host, domain, domains[domain]
        raise AssertionError('Cannot find domain for route %s' % route)

    def _upload_application(self, app, path):
        _logger.debug('Uploading application %s', app['entity']['name'])
        if os.path.isfile(path):
            self._upload_application_zip(app, path)
        elif os.path.isdir(path):
            self._upload_application_directory(app, path)
        else:
            raise AssertionError('Path %s is neither a directory nor a file' % path)

    def _upload_application_zip(self, app, path):
        _logger.debug('Unzipping file %s', path)
        tmp_dir = tempfile.mkdtemp()
        try:
            FileHelper.unzip(path, tmp_dir)
            self._upload_application_directory(app, tmp_dir)
        finally:
            shutil.rmtree(tmp_dir)

    def _upload_application_directory(self, app, path):
        _logger.debug('Uploading application from directory %s', path)
        _, temp_file = tempfile.mkstemp()
        try:
            resource_descriptions_by_path = PushOperation._load_all_resources(path)

            def generate_key(item):
                return '%s-%d' % (item["sha1"], item["size"])

            already_uploaded_entries = [generate_key(item) for item in
                                        self.client.v2.resources.match([dict(sha1=item["sha1"], size=item["size"])
                                                                        for item in
                                                                        resource_descriptions_by_path.values()])]
            _logger.debug('Already uploaded %d / %d items',
                          len(already_uploaded_entries), len(resource_descriptions_by_path))

            FileHelper.zip(temp_file, path,
                           lambda item: generate_key(
                               resource_descriptions_by_path[item]) not in already_uploaded_entries)
            _logger.debug('Diff zip file built: %s', temp_file)
            resources = [
                dict(fn=resource_path,
                     sha1=resource_description["sha1"],
                     size=resource_description["size"],
                     mode=resource_description["mode"])
                for resource_path, resource_description in resource_descriptions_by_path.items()
                if generate_key(resource_description) in already_uploaded_entries
            ]
            _logger.debug('Uploading bits of application')
            job = self.client.v2.apps.upload(app['metadata']['guid'],
                                             resources,
                                             temp_file,
                                             True)
            self._poll_job(job)
        finally:
            _logger.debug('Skipping remove of zip file')

    @staticmethod
    def _load_all_resources(path):
        application_items = {}
        for directory, file_names in FileHelper.walk(path):
            for file_name in file_names:
                file_location = os.path.join(path, directory, file_name)
                application_items[os.path.join(directory, file_name)] = dict(
                    sha1=FileHelper.sha1(file_location),
                    size=FileHelper.size(file_location),
                    mode=FileHelper.mode(file_location))
        return application_items

    def _bind_services(self, space, app, services):
        service_instances = [service_instance for service_instance in space.service_instances(
            return_user_provided_service_instances="true")]
        service_name_to_instance_guid = {service_instance["entity"]["name"]: service_instance["metadata"]["guid"]
                                         for service_instance in service_instances}
        existing_service_instance_guid = [service_binding['entity']['service_instance_guid']
                                          for service_binding in app.service_bindings()]
        for service_name in services:
            service_instance_guid = service_name_to_instance_guid.get(service_name)
            if service_instance_guid is None:
                raise AssertionError('No service found with name %s' % service_name)
            elif service_instance_guid in existing_service_instance_guid:
                _logger.debug('%s already bound to %s', app["entity"]["name"], service_name)
            else:
                _logger.debug('Binding %s to %s', app["entity"]["name"], service_name)
                self.client.v2.service_bindings.create(app['metadata']['guid'], service_instance_guid)

    @staticmethod
    def _restart_application(app):
        _logger.debug("Restarting application")
        app.stop()
        app.start()

    def _poll_job(self, job):
        def job_not_ended(j):
            return j['entity']['status'] in ['queued', 'running']

        job_guid = job['metadata']['guid']
        _logger.debug('Waiting for upload of application to be complete. Polling job %s...', job_guid)
        started_time = time.time()
        elapsed_time = 0

        while job_not_ended(job) and elapsed_time < PushOperation.UPLOAD_TIMEOUT:
            _logger.debug('Getting job status %s..', job_guid)
            job = self.client.v2.jobs.get(job_guid)
            if job_not_ended(job):
                time.sleep(5)
                elapsed_time = int(time.time() - started_time)
        if job_not_ended(job):
            raise AssertionError('Exceeded timeout while polling job of upload')
        elif job['entity']['status'] == 'failed':
            raise AssertionError('Job of upload exceeded in error: %s', json.dumps(job['entity']['error_details']))
        else:
            _logger.debug('Job ended with status %s', job['entity']['status'])
