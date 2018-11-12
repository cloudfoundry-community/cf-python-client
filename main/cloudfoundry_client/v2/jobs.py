from cloudfoundry_client.json_object import JsonObject


class JobManager(object):
    def __init__(self, target_endpoint, client):
        self.target_endpoint = target_endpoint
        self.client = client

    def get(self, job_guid):
        return self.client.get('%s/v2/jobs/%s' % (self.target_endpoint, job_guid)).json(object_pairs_hook=JsonObject)
