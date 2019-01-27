import os
import shutil
import tempfile
import zipfile
from unittest import TestCase

from cloudfoundry_client.operations.push.file_helper import FileHelper


class TestUnzipHelper(TestCase):
    def setUp(self):
        self.input_dirpath = self.zip_some_data()
        self.output_dirpath = tempfile.mkdtemp()

    def test_unzip(self):
        self.unzip()
        self.assertFileUnzipped()

    def test_unzip_with_existing_output_subdir(self):
        os.makedirs(os.path.join(self.output_dirpath, 'some_dir', 'subdir'))
        self.unzip()

        self.assertFileUnzipped()

    def unzip(self):
        FileHelper.unzip(os.path.join(self.input_dirpath, 'myzip.zip'), self.output_dirpath)

    def zip_some_data(self):
        input_dirpath = self.prepare_data_to_zip()
        with zipfile.ZipFile(os.path.join(input_dirpath, 'myzip.zip'), 'w', zipfile.ZIP_DEFLATED) as myzip:
            myzip.write(os.path.join(input_dirpath, 'file.txt'), 'file.txt')
            myzip.write(os.path.join(input_dirpath, 'some_dir'), 'some_dir')
            myzip.write(os.path.join(input_dirpath, 'some_dir', 'subdir'), 'some_dir/subdir')
        return input_dirpath

    def prepare_data_to_zip(self):
        input_dirpath = tempfile.mkdtemp()
        shutil.copyfile(__file__, os.path.join(input_dirpath, 'file.txt'))
        os.makedirs(os.path.join(input_dirpath, 'some_dir', 'subdir'))
        shutil.copyfile(__file__, os.path.join(input_dirpath, 'some_dir', 'file.txt'))
        return input_dirpath

    def assertFileUnzipped(self):
        self.assertTrue(os.path.isfile(os.path.join(self.output_dirpath, 'file.txt')))
        self.assertTrue(os.path.isdir(os.path.join(self.output_dirpath, 'some_dir')))
        self.assertTrue(os.path.isdir(os.path.join(self.output_dirpath, 'some_dir', 'subdir')))
