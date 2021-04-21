from functools import partial, reduce
from typing import Callable, List, Tuple, Any, Optional, Generator, TYPE_CHECKING
from urllib.parse import quote
from requests import Response

from cloudfoundry_client.errors import InvalidEntity
from cloudfoundry_client.json_object import JsonObject
from cloudfoundry_client.request_object import Request

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient


class Entity(JsonObject):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient", *args, **kwargs):
        super(Entity, self).__init__(*args, **kwargs)
        self.target_endpoint = target_endpoint
        self.client = client
        try:
            if not (isinstance(self.get("entity"), dict)):
                raise InvalidEntity(**self)

            for attribute, value in list(self["entity"].items()):
                domain_name, suffix = attribute.rpartition("_")[::2]
                if suffix == "url":
                    manager_name = domain_name if domain_name.endswith("s") else "%ss" % domain_name
                    try:
                        other_manager = getattr(client.v2, manager_name)
                    except AttributeError:
                        # generic manager

                        other_manager = EntityManager(target_endpoint, client, "")
                    if domain_name.endswith("s"):
                        new_method = partial(other_manager._list, value)
                    else:
                        new_method = partial(other_manager._get, value)
                    new_method.__name__ = domain_name
                    setattr(self, domain_name, new_method)
        except KeyError:
            raise InvalidEntity(**self)


EntityBuilder = Callable[[List[Tuple[str, Any]]], Entity]

PaginateEntities = Generator[Entity, None, None]


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

    def _list(self, requested_path: str, entity_builder: Optional[EntityBuilder] = None, **kwargs) -> PaginateEntities:
        url_requested = self._get_url_filtered("%s%s" % (self.target_endpoint, requested_path), **kwargs)
        response = self.client.get(url_requested)
        entity_builder = self._get_entity_builder(entity_builder)
        while True:
            response_json = self._read_response(response, JsonObject)
            for resource in response_json["resources"]:
                yield entity_builder(list(resource.items()))
            if response_json["next_url"] is None:
                break
            else:
                url_requested = "%s%s" % (self.target_endpoint, response_json["next_url"])
                response = self.client.get(url_requested)

    def _create(self, data: dict, **kwargs) -> Entity:
        url = "%s%s" % (self.target_endpoint, self.entity_uri)
        return self._post(url, data, **kwargs)

    def _update(self, resource_id: str, data: dict, **kwargs):
        url = "%s%s/%s" % (self.target_endpoint, self.entity_uri, resource_id)
        return self._put(url, data, **kwargs)

    def _remove(self, resource_id: str, **kwargs):
        url = "%s%s/%s" % (self.target_endpoint, self.entity_uri, resource_id)
        self._delete(url, **kwargs)

    def _get(self, requested_path: str, entity_builder: Optional[EntityBuilder] = None) -> Entity:
        url = "%s%s" % (self.target_endpoint, requested_path)
        response = self.client.get(url)
        return self._read_response(response, entity_builder)

    def _post(self, url: str, data: Optional[dict] = None, **kwargs):
        response = self.client.post(url, json=data, **kwargs)
        return self._read_response(response)

    def _put(self, url: str, data: Optional[dict] = None, **kwargs):
        response = self.client.put(url, json=data, **kwargs)
        return self._read_response(response)

    def _delete(self, url: str, **kwargs):
        self.client.delete(url, **kwargs)

    def __iter__(self) -> PaginateEntities:
        return self.list()

    def __getitem__(self, entity_guid) -> Entity:
        return self.get(entity_guid)

    def list(self, **kwargs) -> PaginateEntities:
        return self._list(self.entity_uri, **kwargs)

    def get_first(self, **kwargs) -> Optional[Entity]:
        kwargs.setdefault("results-per-page", 1)
        for entity in self._list(self.entity_uri, **kwargs):
            return entity
        return None

    def get(self, entity_id: str, *extra_paths) -> Entity:
        if len(extra_paths) == 0:
            requested_path = "%s/%s" % (self.entity_uri, entity_id)
        else:
            requested_path = "%s/%s/%s" % (self.entity_uri, entity_id, "/".join(extra_paths))
        return self._get(requested_path)

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
