import os
import shutil
import subprocess
import sys

from setuptools import setup, find_packages, Command

src_dir = 'src/python'
package_directory = 'cloudfoundry_client'
package_name = 'cloudfoundry-client'
loggregator_dir = 'loggregator'
sys.path.insert(0, os.path.realpath(src_dir))

version_file = '%s/%s/__init__.py' % (src_dir, package_directory)
with open(version_file, 'r') as f:
    for line in f.readlines():
        if line.find('__version__') >= 0:
            exec line
            break
    else:
        raise AssertionError('Failed to load version from %s' % version_file)


def purge_sub_dir(path):
    shutil.rmtree(os.path.join(os.path.dirname(__file__), path))


class GenerateCommand(Command):
    description = "generate protobuf class generation"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        source_path = os.path.join(os.path.dirname(__file__), src_dir, package_directory, loggregator_dir)
        for file_protobuf in os.listdir(source_path):
            if file_protobuf.endswith('.proto'):
                print('Generating %s' % file_protobuf)
                subprocess.call(['protoc', '-I', source_path, '--python_out=%s' % source_path,
                                 os.path.join(source_path, file_protobuf)])


setup(name=package_name,
      version=__version__,
      zip_safe=True,
      packages=find_packages(where=src_dir),
      author='Benjamin Einaudi',
      author_email='antechrestos@gmail.com',
      description='A client library for CloudFoundry',
      long_description=open('README.md').read(),
      url='http://github.com/antechrestos/cf-python-client',
      classifiers=[
          "Programming Language :: Python",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.7",
          "Topic :: Communications",
      ],
      entry_points={
          'console_scripts': [
              'cloudfoundry-client = %s.main:main' % package_directory,
          ]
      },
      cmdclass=dict(generate=GenerateCommand),
      package_dir={package_directory: '%s/%s' % (src_dir, package_directory)},
      install_requires=[requirement.rstrip(' \r\n') for requirement in open('requirements.txt')],
      tests_require=[line.rstrip() for line in open('test/requirements.txt')],
      test_suite='test',
      )
