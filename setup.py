from setuptools import setup, find_packages

src_dir = 'src'
package_directory = 'cloudfoundry_client'
package_name = 'cloudfoundry-client'


__version__ = None
version_file = '%s/%s/__init__.py' % (src_dir, package_directory)
with open(version_file, 'r') as f:
    for line in f.readlines():
        if line.find('__version__') >= 0:
            exec line

if __version__ is None:
    raise AssertionError('Failed to load version from %s' % version_file)

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
          ],
      },
      package_dir={package_directory: '%s/%s' % (src_dir, package_directory)},
      install_requires=[requirement.rstrip(' \r\n') for requirement in open('requirements.txt').readlines()]
      )
