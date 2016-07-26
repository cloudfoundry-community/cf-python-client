cf-python-client [![pypi](https://img.shields.io/pypi/v/cloudfoundry-client.svg)]() [![license](https://img.shields.io/github/license/antechrestos/rest-client-test.svg)]()
================

The cf-python-client repo contains a Python client library for Cloud Foundry. 

## Packaging

To build the library run :

```
$ python setup.py install
```

## Run the client

To run the client, enter the following command :

```
$ cloudfoundry-client
```

This will explains you how the client works. At first execution, it will ask you information about the platform you want to reach (url, login and so on).
Please note that your credentials won't be saved on your disk: only tokens will be kept for further use.