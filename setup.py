from setuptools import setup, find_packages

src_dir = 'src'
package_name = 'cloudfoundry-client'

static_files = ['README.md']

setup(name=package_name,
      version='0.0.1',
      zip_safe=True,
      packages=find_packages(where=src_dir),
      author='Benjamin Einaudi',
      author_email='antechrestos@gmail.com',
      description='A client library for CloudFoundry',
      long_description=open('README.md').read(),
      url='http://github.com/antechrestos/cf-python-client',
      classifiers=[
          "Programming Language :: Python",
          "Development Status :: 1 - Planning",
          "License :: OSI Approved",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.7",
          "Topic :: Communications",
      ],
      entry_points={
          'console_scripts': [
              'cloudfoundry-client = cloudfoundry.main:main',
          ],
      },

      include_package_data=True,
      package_dir={package_name: '%s/%s' % (src_dir, package_name)},
      package_data={package_name: static_files},
      install_requires=[requirement.rstrip(' \r\n') for requirement in open('requirements.txt').readlines()]
      )
