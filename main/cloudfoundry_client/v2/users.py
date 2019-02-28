from cloudfoundry_client.json_object import JsonObject


class UserManager(object):
    def __init__(self, target_endpoint, client):
        super(UserManager, self).__init__(target_endpoint, client, '/v2/users')
