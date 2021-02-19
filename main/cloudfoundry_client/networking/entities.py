import logging
from functools import reduce
from typing import Callable, List, Tuple, Any, Optional, Generator, TYPE_CHECKING
from urllib.parse import quote

from requests import Response

from cloudfoundry_client.errors import InvalidEntity
from cloudfoundry_client.json_object import JsonObject
from cloudfoundry_client.request_object import Request

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient

_logger = logging.getLogger(__name__)


class Entity(JsonObject):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient", *args, **kwargs):
        super(Entity, self).__init__(*args, **kwargs)
        self.target_endpoint = target_endpoint
        self.client = client
        try:
            src = self["source"]
            dst = self["destination"]
            src["id"]
            dst["id"]
            dst["protocol"]
            dst["ports"]["start"]
            dst["ports"]["end"]
        except KeyError:
            raise InvalidEntity(**self)


EntityBuilder = Callable[[List[Tuple[str, Any]]], Entity]


class EntityManager(object):
    list_query_parameters = ["page", "results-per-page", "order-direction"]

    list_multi_parameters = ["order-by"]

    def __init__(
        self, target_endpoint: str, client: "CloudFoundryClient", entity_uri: str, entity_builder: Optional[EntityBuilder] = None
    ):
        self.target_endpoint = target_endpoint
        self.entity_uri = entity_uri
        self.client = client
        self.entity_builder = (
            entity_builder if entity_builder is not None else lambda pairs: Entity(target_endpoint, client, pairs)
        )

    def _list(
        self, requested_path: str, entity_builder: Optional[EntityBuilder] = None, **kwargs
    ) -> Generator[Entity, None, None]:
        url_requested = self._get_url_filtered("%s%s" % (self.target_endpoint, requested_path), **kwargs)
        response = self.client.get(url_requested)
        entity_builder = self._get_entity_builder(entity_builder)
        _logger.debug("GET - %s - %s", url_requested, response.text)
        response_json = self._read_response(response, JsonObject)
        for resource in response_json["policies"]:
            yield entity_builder(list(resource.items()))

    def _create(self, data: dict, **kwargs) -> Entity:
        url = "%s%s" % (self.target_endpoint, self.entity_uri)
        return self._post(url, data, **kwargs)

    def _remove(self, resource_id: str, **kwargs):
        url = "%s%s/%s" % (self.target_endpoint, self.entity_uri, resource_id)
        self._delete(url, **kwargs)

    def _post(self, url: str, data: Optional[dict] = None, **kwargs):
        response = self.client.post(url, json=data, **kwargs)
        _logger.debug("POST - %s - %s", url, response.text)
        return self._read_response(response)

    def _delete(self, url: str, **kwargs):
        response = self.client.delete(url, **kwargs)
        _logger.debug("DELETE - %s - %s", url, response.text)

    def __iter__(self) -> Generator[Entity, None, None]:
        return self.list()

    def list(self, **kwargs) -> Generator[Entity, None, None]:
        return self._list(self.entity_uri, **kwargs)

    def get_first(self, **kwargs) -> Optional[Entity]:
        kwargs.setdefault("results-per-page", 1)
        for entity in self._list(self.entity_uri, **kwargs):
            return entity
        return None

    def _read_response(self, response: Response, other_entity_builder: Optional[EntityBuilder] = None):
        entity_builder = self._get_entity_builder(other_entity_builder)
        result = response.json(object_pairs_hook=JsonObject)
        return entity_builder(list(result.items()))

    @staticmethod
    def _request(**mandatory_parameters) -> Request:
        return Request(**mandatory_parameters)

    def _get_entity_builder(self, entity_builder: Optional[EntityBuilder]) -> EntityBuilder:
        if entity_builder is None:
            return self.entity_builder
        else:
            return entity_builder

    def _get_url_filtered(self, url: str, **kwargs) -> str:
        def _append_encoded_parameter(parameters: List[str], args: Tuple[str, Any]) -> List[str]:
            parameter_name, parameter_value = args[0], args[1]
            if parameter_name in self.list_query_parameters:
                parameters.append("%s=%s" % (parameter_name, str(parameter_value)))
            elif parameter_name in self.list_multi_parameters:
                value_list = parameter_value
                if not isinstance(value_list, (list, tuple)):
                    value_list = [value_list]
                for value in value_list:
                    parameters.append("%s=%s" % (parameter_name, str(value)))
            elif isinstance(parameter_value, (list, tuple)):
                parameters.append("q=%s" % quote("%s IN %s" % (parameter_name, ",".join(parameter_value))))
            else:
                parameters.append("q=%s" % quote("%s:%s" % (parameter_name, str(parameter_value))))
            return parameters

        if len(kwargs) > 0:
            return "%s?%s" % (url, "&".join(reduce(_append_encoded_parameter, sorted(list(kwargs.items())), [])))
        else:
            return url
