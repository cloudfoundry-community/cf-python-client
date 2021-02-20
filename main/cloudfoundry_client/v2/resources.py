from typing import List, TYPE_CHECKING

from cloudfoundry_client.json_object import JsonObject

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class ResourceManager(object):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient"):
        self.target_endpoint = target_endpoint
        self.client = client

    def match(self, items: List[dict]) -> List[JsonObject]:
        response = self.client.put("%s/v2/resource_match" % self.client.info.api_endpoint, json=items)
        return response.json(object_pairs_hook=JsonObject)
