from typing import TYPE_CHECKING

from cloudfoundry_client.json_object import JsonObject

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class JobManager(object):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        self.target_endpoint = target_endpoint
        self.client = client

    def get(self, job_guid: str) -> JsonObject:
        return self.client.get("%s/v2/jobs/%s" % (self.target_endpoint, job_guid)).json(object_pairs_hook=JsonObject)
