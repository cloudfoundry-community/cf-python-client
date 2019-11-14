import os
from unittest import TestCase
from unittest.mock import mock_open, patch

from cloudfoundry_client.operations.push.cf_ignore import CfIgnore


class TestCfIgnore(TestCase):

    def test_open_cfignore_file(self):
        with patch("builtins.open", mock_open(read_data="*.log")) as mock_file, \
                patch('os.path.isfile', create=True) as mock_isfile:
            mock_isfile.__return_value__ = True
            application_path = '/some/path'
            CfIgnore(application_path)

            mock_file.assert_called_with(os.path.join(application_path, '.cfignore'), 'r')

    def test_ignore_wildcard_resources(self):
        with patch("builtins.open", mock_open(read_data="*.log")), \
             patch('os.path.isfile', create=True) as mock_isfile:
            mock_isfile.__return_value__ = True
            cf_ignore = CfIgnore('/some/path')

            self.assertTrue(cf_ignore.is_entry_ignored("toto.log"))
            self.assertTrue(cf_ignore.is_entry_ignored("/some/other/path/toto.log"))

    def test_ignore_directory(self):
        with patch("builtins.open", mock_open(read_data="ignored/directory/")), \
             patch('os.path.isfile', create=True) as mock_isfile:
            mock_isfile.__return_value__ = True
            cf_ignore = CfIgnore('/some/path')

            self.assertTrue(cf_ignore.is_entry_ignored("ignored/directory/resource.file"))
            self.assertTrue(cf_ignore.is_entry_ignored("/ignored/directory/resource.file"))
            self.assertTrue(
                cf_ignore.is_entry_ignored("/some/sub/directory/containing/ignored/directory/resource.file"))
            # File in fact
            self.assertFalse(cf_ignore.is_entry_ignored('/ignored/directory'))

    def test_ignore_file_with_directory(self):
        with patch("builtins.open", mock_open(read_data="ignored/directory/resource.file")), \
             patch('os.path.isfile', create=True) as mock_isfile:
            mock_isfile.__return_value__ = True
            cf_ignore = CfIgnore('/some/path')

            self.assertTrue(cf_ignore.is_entry_ignored("ignored/directory/resource.file"))
            self.assertTrue(cf_ignore.is_entry_ignored("/ignored/directory/resource.file"))
            self.assertTrue(
                cf_ignore.is_entry_ignored("/some/sub/directory/containing/ignored/directory/resource.file"))
            # File in fact
            self.assertFalse(cf_ignore.is_entry_ignored('ignored/resource.file'))
