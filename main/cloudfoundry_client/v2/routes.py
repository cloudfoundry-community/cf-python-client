from cloudfoundry_client.v2.entities import EntityManager


class RouteManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(RouteManager, self).__init__(target_endpoint, client, '/v2/routes')

    def create_tcp_route(self, domain_guid, space_guid, port=None):
        request = dict(domain_guid=domain_guid, space_guid=space_guid)
        if port is None:
            return super(RouteManager, self)._create(request, params=dict(generate_port=True))
        else:
            request['port'] = port
            return super(RouteManager, self)._create(request)

    def create_host_route(self, domain_guid, space_guid, host, path=''):
        request = dict(domain_guid=domain_guid, space_guid=space_guid, host=host, path=path)
        return super(RouteManager, self)._create(request)
