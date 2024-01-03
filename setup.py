import os
import shutil
import subprocess
import sys

from setuptools import setup, find_packages, Command, __version__

src_dir = "main"
package_directory = "cloudfoundry_client"
package_name = "cloudfoundry-client"
dropsonde_src = "vendors/dropsonde-protocol"
dropsonde_dest = "dropsonde"
sys.path.insert(0, os.path.realpath(src_dir))

version_file = "%s/%s/__init__.py" % (src_dir, package_directory)
with open(version_file, "r") as f:
    for line in f.readlines():
        if line.find("__version__") >= 0:
            exec(line)
            break
    else:
        raise AssertionError("Failed to load version from %s" % version_file)


def purge_sub_dir(path):
    shutil.rmtree(os.path.join(os.path.dirname(__file__), path))


if "test" in sys.argv[1:]:
    print("%s added" % os.path.join(os.getcwd(), "test"))
    sys.path.append(os.path.join(os.getcwd(), "test"))


class GenerateCommand(Command):
    description = "generate protobuf class generation"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        source_path = os.path.join(os.path.dirname(__file__), dropsonde_src)
        for file_protobuf in os.listdir(source_path):
            if file_protobuf.endswith(".proto"):
                file_path = os.path.join(source_path, file_protobuf)
                dest_path = os.path.join(src_dir, package_directory, dropsonde_dest)
                print("Generating %s from %s to %s" % (file_protobuf, file_path, dest_path))
                subprocess.call(
                    [
                        "protoc",
                        "--proto_path",
                        source_path,
                        "--python_out=%s" % dest_path,
                        file_path,
                    ]
                )


setup(
    name=package_name,
    version=__version__,
    zip_safe=True,
    packages=find_packages(where=src_dir),
    author="Benjamin Einaudi",
    author_email="antechrestos@gmail.com",
    description="A client library for CloudFoundry",
    long_description=open("README.rst").read(),
    url="http://github.com/antechrestos/cf-python-client",
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications",
    ],
    entry_points={
        "console_scripts": [
            "cloudfoundry-client = %s.main.main:main" % package_directory,
        ]
    },
    cmdclass=dict(generate=GenerateCommand),
    package_dir={package_directory: "%s/%s" % (src_dir, package_directory)},
    install_requires=[requirement.rstrip(" \r\n") for requirement in open("requirements.txt")],
    test_suite="test",
)
