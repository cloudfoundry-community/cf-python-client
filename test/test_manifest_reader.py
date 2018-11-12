import os
import unittest

from cloudfoundry_client.operations.push.validation.manifest import ManifestReader


class TestManifestReader(unittest.TestCase):
    def test_name_should_be_set(self):
        manifest = dict(path='test/')
        self.assertRaises(AssertionError, lambda: ManifestReader._validate_application_manifest('.', manifest))

    def test_application_should_declare_either_path_or_docker(self):
        manifest = dict(name='the-name', docker=dict(), path='test/')
        self.assertRaises(AssertionError, lambda: ManifestReader._validate_application_manifest('.', manifest))

    def test_application_should_declare_at_least_path_or_docker(self):
        manifest = dict(name='the-name', routes=[], environment=dict())
        self.assertRaises(AssertionError, lambda: ManifestReader._validate_application_manifest('.', manifest))

    def test_deprecated_entries_should_not_be_set(self):
        for deprecated in ['host', 'hosts', 'domain', 'domains', 'no-hostname']:
            manifest = dict(name='the-name', path='test/')
            manifest[deprecated] = 'some-value'
            self.assertRaises(AssertionError, lambda: ManifestReader._validate_application_manifest('.', manifest))

    def test_docker_manifest_should_declare_buildpack_or_image(self):
        manifest = dict(name='the-name', docker=dict(image='some-image', buildpack='some-buildpack'))
        self.assertRaises(AssertionError, lambda: ManifestReader._validate_application_manifest('.', manifest))

    def test_username_should_be_set_if_password_is(self):
        manifest = dict(name='the-name', docker=dict(image='some-image', password='P@SsW0r$'))
        self.assertRaises(AssertionError, lambda: ManifestReader._validate_application_manifest('.', manifest))

    def test_password_should_be_set_if_username_is(self):
        manifest = dict(name='the-name', docker=dict(image='some-image', username='the-user'))
        self.assertRaises(AssertionError, lambda: ManifestReader._validate_application_manifest('.', manifest))

    def test_username_and_password_are_set_when_image_is(self):
        manifest = dict(name='the-name', docker=dict(username='the-user', password='P@SsW0r$'))
        self.assertRaises(AssertionError, lambda: ManifestReader._validate_application_manifest('.', manifest))

    def test_routes_should_be_an_object_with_attribute(self):
        manifest = dict(name='the-name', path='test/', routes=['a route'])
        self.assertRaises(AssertionError, lambda: ManifestReader._validate_application_manifest('.', manifest))
        manifest = dict(name='the-name', path='test/', routes=[dict(invalid_attribute='any-value')])
        self.assertRaises(AssertionError, lambda: ManifestReader._validate_application_manifest('.', manifest))

    def test_valid_application_with_path_and_routes(self):
        manifest = dict(name='the-name', path='test/', routes=[dict(route='first-route'), dict(route='second-route')])
        ManifestReader._validate_application_manifest('.', manifest)

    def test_valid_application_with_docker_and_routes(self):
        manifest = dict(docker=dict(username='ther-user', password='P@SsW0r$', image='some-image'),
                        name='the-name', routes=[dict(route='first-route'), dict(route='second-route')])
        ManifestReader._validate_application_manifest('.', manifest)

    def path_should_be_set_as_absolute(self):
        manifest = dict(name='the-name', path='test/')
        ManifestReader._validate_application_manifest('.', manifest)
        self.assertEqual(os.path.abspath('test'), manifest['path'])

    def test_memory_in_kb(self):
        manifest = dict(memory='2048KB')
        ManifestReader._convert_memory(manifest)
        self.assertEqual(2, manifest['memory'])

    def test_memory_in_mb(self):
        manifest = dict(memory='2048MB')
        ManifestReader._convert_memory(manifest)
        self.assertEqual(2048, manifest['memory'])

    def test_memory_in_gb(self):
        manifest = dict(memory='1G')
        ManifestReader._convert_memory(manifest)
        self.assertEqual(1024, manifest['memory'])