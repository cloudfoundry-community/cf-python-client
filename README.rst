Cloudfoundry python client
==========================
.. image:: https://img.shields.io/pypi/v/cloudfoundry-client.svg
    :target: https://pypi.python.org/pypi/cloudfoundry-client

.. image:: https://img.shields.io/github/license/antechrestos/cf-python-client.svg
    :target: https://raw.githubusercontent.com/antechrestos/cf-python-client/master/LICENSE

The cf-python-client repo contains a Python client library for Cloud Foundry. 

Installing
----------

Supported versions
~~~~~~~~~~~~~~~~~~

:warning: Starting version ``1.11.0``, versions older that python ``3.6.0`` will not be supported anymore. This late version was released by the end 2016.

For those that are still using python 2.7, it won't be supported by the end of 2020 and all library shall stop supporting it.

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
To instantiate the client, nothing easier

.. code-block:: python

    from cloudfoundry_client.client import CloudFoundryClient
    target_endpoint = 'https://somewhere.org'
    proxy = dict(http=os.environ.get('HTTP_PROXY', ''), https=os.environ.get('HTTPS_PROXY', ''))
    client = CloudFoundryClient(target_endpoint, proxy=proxy, verify=False)
    # init with user credentials
    client.init_with_user_credentials('login', 'password')
    # init with refresh token (that will retrieve a fresh access token)
    client.init_with_token('refresh-token')
    # init with access and refresh token (if the above method is not convenient)
    client.refresh_token = 'refresh-token'
    client._access_token = 'access-token'

It can also be instantiated with oauth code flow if you possess a dedicated oauth application with its redirection

.. code-block:: python

    from flask import request
    from cloudfoundry_client.client import CloudFoundryClient
    target_endpoint = 'https://somewhere.org'
    proxy = dict(http=os.environ.get('HTTP_PROXY', ''), https=os.environ.get('HTTPS_PROXY', ''))
    client = CloudFoundryClient(target_endpoint, proxy=proxy, verify=False, client_id='my-client-id', client_secret='my-client-secret')

    @app.route('/login')
    def login():
        global client
        return redirect(client.generate_authorize_url('http://localhost:9999/code', '666'))

    @app.route('/code')
    def code():
        global client
        client.init_authorize_code_process('http://localhost:9999/code', request.args.get('code'))


And then you can use it as follows:

.. code-block:: python

    for organization in client.v2.organizations:
        print(organization['metadata']['guid'])

API V2
-------

Entities
~~~~~~~~
Entities returned by api V2 calls (*organization*, *space*, *app*..) are navigable ie you can call the method associated with the *xxx_url* entity attribute
(note that if the attribute's name ends with a list, it will be interpreted as a list of object. Other wise you will get a single entity).

.. code-block:: python

    for organization in client.v2.organizations:
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

    for app in client.v2.apps:
        print(app.summary())

Available managers
~~~~~~~~~~~~~~~~~~
So far the implemented managers that are available are:

- ``service_plans``
- ``service_plan_visibilities``
- ``service_instances``
- ``service_keys``
- ``service_bindings``
- ``service_brokers``
- ``apps``
- ``events``
- ``buildpacks``
- ``organizations``
- ``spaces``
- ``services``
- ``routes``
- ``shared_domains``
- ``private_domains``
- ``security_groups``

Note that even if, while navigating, you reach an entity manager that does not exist, the get will be performed and you will get the expected entities.
For example, event entity manager is not yet implemented but you can do

.. code-block:: python

    for app in client.v2.apps:
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
    org_get = client.v2.organizations.get('test-org-guid')
    org_get_first = client.v2.organizations.get_first(**{'name': 'test-org'})
    org_from_list = list(client.v2.organizations.list(**{'name': 'test-org'}))[0]
    assert org_get == org_get_first == org_from_list

    # You can also specify multiple values for a query parameter.
    for organization in client.v2.organizations.list(**{'name': ['org1', 'org2']}):
        print(organization['metadata']['guid'])

    # Order and Paging parameters are also supported.
    query = {
    	'order-by': 'name',
    	'order-direction': 'desc',
    	'results-per-page': 100
    }
    for organization in client.v2.organizations.list(**query):
        print(organization['entity']['name'])

API V3
------

Entities
~~~~~~~~

Entities returned by API V3 calls transcripts links by providing a call on the object with the name of the link itself.
Let's explain it with the next code

.. code-block:: python

  for app in client.v3.apps.list(space_guids='space_guid'):
    for task in app.tasks():
        print('Task %s' % task['guid'])
    app.stop()
    space = app.space()

Another example:

.. code-block:: python

    app = client.v3.apps['app-guid']
    for task in app.tasks():
        task.cancel()
    for task in client.v3.tasks.list(app_guids=['app-guid-1', 'app-guid-2']):
        task.cancel()

When supported by the API, parent entities can be included in a single call. The included entities replace the links mentioned above.
The following code snippet issues three requests to the API in order to get app, space and organization data:

.. code-block:: python

  app = client.v3.apps.get("app-guid")
  print("App name: %s" % app["name"])
  space = app.space()
  print("Space name: %s" % space["name"])
  org = space.organization()
  print("Org name: %s" % org["name"])

By changing the first line only, a single request fetches all the data. The navigation from app to space and space to organization remains unchanged.

.. code-block:: python

  app = client.v3.apps.get("app-guid", include="space.organization")

Available managers on API V3 are:

- ``apps``
- ``buildpacks``
- ``domains``
- ``feature_flags``
- ``isolation_segments``
- ``jobs``
- ``organizations``
- ``organization_quotas``
- ``processes``
- ``service_brokers``
- ``service_credential_bindings``
- ``service_instances``
- ``service_offerings``
- ``service_plans``
- ``spaces``
- ``tasks``

The managers provide the same methods as the V2 managers with the following differences:

- ``get(**kwargs)``: supports keyword arguments that are passed on to the API, e.g. "include"


Networking
----------

policy server
~~~~~~~~~~~~~

At the moment we have only the network policies implemented

.. code-block:: python

  for policy in client.network.v1.external.policies.list():
    print('destination protocol = {}'.format(policy['destination']['protocol']))
    print('destination from port = {}'.format(policy['destination']['ports']['start']))
    print('destination to port = {}'.format(policy['destination']['ports']['end']))


Available managers on API V3 are:

- ``policy``

This manager provides:

- ``list(**kwargs)``: return an *iterator* on entities, according to the given filtered parameters
- ``__iter__``: iteration on the manager itself. Alias for a no-filter list
- ``_create``: the create operation. Since it is a generic operation (only takes a *dict* object), this operation is protected
- ``_remove``: the delete operation. This operation is maintained protected.


Application logs
----------------

Recent logs of an application can be get as follows:

.. code-block:: python

    app = client.v2.apps['app-guid']
    for log in app.recent_logs():
        print(log)


Logs can also be streamed using a websocket as follows:

.. code-block:: python

    app = client.v2.apps['app-guid']
    for log in app.stream_logs():
        # read message infinitely (use break to exit... it will close the underlying websocket)
        print(log)
    # or
    for log in client.doppler.stream_logs('app-guid'):
        # read message infinitely (use break to exit... it will close the underlying websocket)
        print(log)

..

Logs can also be streamed directly from RLP Gateway:

.. code-block:: python

    import asyncio
    from cloudfoundry_client.client import CloudFoundryClient

    target_endpoint = 'https://somewhere.org'
    proxy = dict(http=os.environ.get('HTTP_PROXY', ''), https=os.environ.get('HTTPS_PROXY', ''))
    rlp_client = CloudFoundryClient(target_endpoint, client_id='client_id', client_secret='client_secret', verify=False)
    # init with client credentials
    rlp_client.init_with_client_credentials()

    async def get_logs_for_app(rlp_client, app_guid):
        async for log in rlp_client.rlpgateway.stream_logs(app_guid,
                                                           params={'counter': '', 'gauge': ''},
                                                           headers={'User-Agent': 'cf-python-client'})):
            print(log)

    loop = asyncio.get_event_loop()
    loop.create_task(get_logs_for_app(rlp_client, "app_guid"))
    loop.run_forever()
    loop.close()
..

Command Line Interface
----------------------

The client comes with a command line interface. Run ``cloudfoundry-client`` command. At first execution, it will ask you information about the target platform and your credential (do not worry they are not saved). After that you may have a help by running ``cloudfoundry-client -h``

Operations (experimental)
-------------------------

For now the only operation that is implemented is the push one.

.. code-block:: python

    from cloudfoundry_client.operations.push.push import PushOperation
    operation = PushOperation(client)
    operation.push(client.v2.spaces.get_first(name='My Space')['metadata']['guid'], path)


Issues and contributions
------------------------

Please submit issue/pull request.

You can run tests by doing so. In the project directory:

.. code-block:: bash

    $ export PYTHONPATH=main
    $ python -m unittest discover test
    # or even
    $ python setup.py test
