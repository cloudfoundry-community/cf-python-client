Cloudfoundry python client
==========================
.. image:: https://img.shields.io/pypi/v/cloudfoundry-client.svg
    :target: https://pypi.python.org/pypi/cloudfoundry-client
.. image:: https://img.shields.io/github/license/antechrestos/cf-python-client.svg
    :target: https://raw.githubusercontent.com/antechrestos/cf-python-client/master/LICENSE

The cf-python-client repo contains a Python client library for Cloud Foundry. 

Installing
----------

From pip
~~~~~~~~
.. code-block:: bash

    $ pip install cloudfoundry-client

From sources
~~~~~~~~~~~~

To build the library run :

.. code-block:: bash

    $ python setup.py install


Run the client
--------------
To run the client, enter the following command :

.. code-block:: bash

    $ cloudfoundry-client

This will explains you how the client works. At first execution, it will ask you information about the platform you want to reach (url, login and so on).
Please note that your credentials won't be saved on your disk: only tokens will be kept for further use.

Use the client in your code
---------------------------
You may build the client and use it in your code

Client
~~~~~~
To instanciate the client, nothing easier

.. code-block:: python

    from cloudfoundry_client.client import CloudFoundryClient
    target_endpoint = 'https://somewhere.org'
    proxy = dict(http=os.environ.get('HTTP_PROXY', ''), https=os.environ.get('HTTPS_PROXY', ''))
    client = CloudFoundryClient(target_endpoint, proxy=proxy, skip_verification=True)
    client.init_with_user_credentials('login', 'password')

And then you can use it as follows:

.. code-block:: python

    for organization in client.organizations:
        print organization['metadata']['guid']

Entities
~~~~~~~~
Entities returned by client calls (*organization*, *space*, *app*..) are navigable ie you can call the method associated with the *xxx_url* entity attribute
(note that if the attribute's name ends with a list, it will be interpreted as a list of object. Other wise you will get a single entity).

.. code-block:: python

    for organization in client.organizations:
        for space in organization.spaces(): # perform a GET on spaces_url attribute
            organization_reloaded = space.organization()  # perform a GET on organization_url attribute

Application object provides more methods such as
 - instances
 - stats
 - start
 - stop
 - summary

As instance, you can get all the summaries as follows:

Or else:

.. code-block:: python

    for app in client.apps:
        print app.summary()

Available managers
~~~~~~~~~~~~~~~~~~
So far the implemented managers that are available are:

- ``service_plans``
- ``service_instances``
- ``service_keys``
- ``service_bindings``
- ``service_brokers``
- ``apps``
- ``buildpacks``
- ``organizations``
- ``spaces``
- ``services``
- ``routes``
- ``shared_domains``
- ``private_domains``

Note that even if, while navigating, you reach an entity manager that does not exist, the get will be performed and you will get the expected entities.
For example, event entity manager is not yet implemented but you can do

.. code-block:: python

    for app in client.apps:
        for event in app.events():
            handle_event_object()

All managers provide the following methods:

- ``list(**kwargs)``: return an *iterator* on entities, according to the given filtered parameters
- ``get_first(**kwargs)``: return the first matching entity according to the given parameters. Returns ```None`` if none returned
- ``get``: perform a **GET** on the entity. If the entity cannot be find it will raise an exception due to http *NOT FOUND* response status
- ``__iter__``: iteration on the manager itself. Alias for a no-filter list
- ``__getitem__``: alias for the ``get`` operation
- ``_create``: the create operation. Since it is a generic operation (only takes a *dict* object), this operation is protected
- ``_update``: the update operation. Since it is a generic operation (only takes a the resource id and a *dict* object), this operation is protected
- ``_remove``: the delete operation. This operation is maintained protected.

.. code-block:: python

    # Assume you have an organization named `test-org` with a guid of `test-org-guid`
    org_get = client.organizations.get('test-org-guid')
    org_get_first = client.organizations.get_first(**{'name': 'test-org'})
    org_from_list = list(client.organizations.list(**{'name': 'test-org'}))[0]
    assert org_get == org_get_first == org_from_list

    # You can also specify multiple values for a query parameter.
    for organization in client.organizations.list(**{'name': ['org1', 'org2']}):
    	print organization['metadata']['guid']

    # Order and Paging parameters are also supported.
    query = {
    	'order-by': 'name',
    	'order-direction': 'desc',
    	'results-per-page': 100
    }
    for organization in client.organizations.list(**query):
    	print organization['entity']['name']

Application logs
----------------

Recent logs of an application can be get as follows:

.. code-block:: python
    app = client.apps['app-guid']
    for log in app.recent_logs():
        print(log)


Logs can also be streamed using a websocket as follows:

.. code-block:: python
    import cloudfoundry_client.droppler.envelope_pb2.Envelope
    app = client.apps['app-guid']
    for log in app.stream_logs():
        # read message infinitely (use break to exit... it will close the underlying websocket)
        print(log)



Command Line Interface
----------------------

The client comes with a command line interface. Run ``cloudfoundry-client`` command. At first execution, it will ask you
 information about the target platform and your credential (do not worry they are not saved). After that you may have a help
by running ``cloudfoundry-client -h``

Issues and contributions
------------------------
Please submit issue/pull request.
