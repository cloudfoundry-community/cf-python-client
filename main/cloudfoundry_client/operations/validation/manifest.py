import yaml


class ManifestReader(object):
    @staticmethod
    def load_application_manifests(manifest_path):
        with open(manifest_path, 'r') as fp:
            manifest = yaml.load(fp)
            ManifestReader._validate_manifest(manifest)
            return manifest['applications']

    @staticmethod
    def _validate_manifest(manifest):
        for app_manifest in manifest['applications']:
            ManifestReader._validate_application_manifest(app_manifest)

    @staticmethod
    def _validate_application_manifest(app_manifest):
        name = app_manifest.get('name')
        if name is None or len(name) == 0:
            raise AssertionError('name must be set')
        docker_manifest = app_manifest.get('docker')
        if docker_manifest is not None:
            if app_manifest.get('path') is not None:
                raise AssertionError('Both path and docker cannot be set')
            ManifestReader._validate_application_docker(docker_manifest)
        elif 'path' not in app_manifest:
            raise AssertionError('One of path or docker must be set')
        if app_manifest.get('hosts') is not None or app_manifest.get('host') \
                or app_manifest.get('domains') is not None or app_manifest.get('domain') \
                or app_manifest.get('no-hostname') is not None:
            raise AssertionError(
                'hosts, host, domains, domain and no-hostname are all deprecated. Use the routes attribute')
        routes = app_manifest.get('routes')
        if routes is not None:
            ManifestReader._validate_routes(routes)

    @staticmethod
    def _validate_routes(routes):
        for route in routes:
            if type(route) != dict or 'route' not in route:
                raise AssertionError('routes attribute must be a list of object containing a route attribute')

    @staticmethod
    def _validate_application_docker(docker_manifest):
        docker_image = docker_manifest.get('image')
        if docker_image is not None and docker_manifest.get('buildpack') is not None:
            raise AssertionError('image and buildpack can not both be set for docker')
        docker_username = docker_manifest.get('username')
        docker_password = docker_manifest.get('password')
        if docker_username is not None and docker_password is None or docker_username is None and docker_password is not None:
            raise AssertionError('Docker username/password must be set together or both be unset')
        if docker_username is not None and docker_password is not None and docker_image is None:
            raise AssertionError('Docker image not set while docker username/password are set')
