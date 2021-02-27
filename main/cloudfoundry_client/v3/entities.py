import functools
import logging
from typing import Any, Generator, Optional, List, Tuple, Union, TypeVar, TYPE_CHECKING
from urllib.parse import quote

from requests import Response

from cloudfoundry_client.errors import InvalidEntity
from cloudfoundry_client.json_object import JsonObject
from cloudfoundry_client.request_object import Request

if TYPE_CHECKING:
    from cloudfoundry_client.client import CloudFoundryClient

_logger = logging.getLogger(__name__)


class Entity(JsonObject):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient", **kwargs):
        super(Entity, self).__init__(**kwargs)
        try:
            def default_method(m, u):
                raise NotImplementedError("Unknown method %s for url %s" % (m, u))
            default_manager = self._default_manager(client, target_endpoint)
            for link_name, link in self.get("links", {}).items():
                if link_name != "self":
                    link_method = link.get("method", "GET").lower()
                    ref = link["href"]
                    manager_name = link_name if link_name.endswith("s") else "%ss" % link_name
                    other_manager = getattr(client.v3, manager_name, default_manager)
                    if link_method == "get":
                        new_method = (
                            functools.partial(other_manager._paginate, ref)
                            if link_name.endswith("s")
                            else functools.partial(other_manager._get, ref)
                        )
                    elif link_method == "post":
                        new_method = functools.partial(other_manager._post, ref)
                    elif link_method == "put":
                        new_method = functools.partial(other_manager._put, ref)
                    elif link_method == "delete":
                        new_method = functools.partial(other_manager._delete, ref)
                    else:
                        new_method = functools.partial(default_method, link_method, ref)
                    new_method.__name__ = link_name
                    setattr(self, link_name, new_method)
        except KeyError:
            raise InvalidEntity(**self)

    @staticmethod
    def _default_manager(client, target_endpoint):
        return EntityManager(target_endpoint, client, "")


PaginateEntities = Generator[Entity, None, None]


class Relationship(JsonObject):
    def __init__(self, guid: Optional[str]):
        super(Relationship, self).__init__(guid=guid)


class ToOneRelationship(JsonObject):
    @staticmethod
    def from_json_object(to_one_relationship: JsonObject):
        if to_one_relationship is None:
            return ToOneRelationship(None)
        data = to_one_relationship.pop("data", None)
        result = ToOneRelationship(None if data is None else data["guid"])
        result.update(to_one_relationship)
        return result

    def __init__(self, guid: Optional[str]):
        super(ToOneRelationship, self).__init__(data=Relationship(guid))
        self.guid = guid


class ToManyRelationship(JsonObject):
    @staticmethod
    def from_json_object(to_many_relations: JsonObject):
        result = ToManyRelationship(*[relation["guid"] for relation in to_many_relations.pop("data")])
        result.update(to_many_relations)
        return result

    def __init__(self, *guids: str):
        super(ToManyRelationship, self).__init__(data=[Relationship(guid) for guid in guids])
        self.guids = list(guids)


ENTITY_TYPE = TypeVar("ENTITY_TYPE", bound=Entity)


class EntityManager(object):
    def __init__(self, target_endpoint: str, client: "CloudFoundryClient", entity_uri: str,
                 entity_type: ENTITY_TYPE = Entity):
        self.target_endpoint = target_endpoint
        self.entity_uri = entity_uri
        self.client = client
        self.entity_type = entity_type

    def _post(self, url: str, data: Optional[dict] = None, files: Any = None,
              entity_type: ENTITY_TYPE = None) -> Entity:
        response = self.client.post(url, json=data, files=files)
        _logger.debug("POST - %s - %s", url, response.text)
        return self._read_response(response, entity_type)

    def _get(self, url: str, entity_type: Optional[ENTITY_TYPE] = None) -> Entity:
        response = self.client.get(url)
        _logger.debug("GET - %s - %s", url, response.text)
        return self._read_response(response, entity_type)

    def _put(self, url: str, data: dict, entity_type: Optional[ENTITY_TYPE] = None) -> Entity:
        response = self.client.put(url, json=data)
        _logger.debug("PUT - %s - %s", url, response.text)
        return self._read_response(response, entity_type)

    def _patch(self, url: str, data: dict, entity_type: Optional[ENTITY_TYPE] = None) -> Entity:
        response = self.client.patch(url, json=data)
        _logger.debug("PATCH - %s - %s", url, response.text)
        return self._read_response(response, entity_type)

    def _delete(self, url: str):
        response = self.client.delete(url)
        _logger.debug("DELETE - %s - %s", url, response.text)

    def _list(self, requested_path: str, entity_type: Optional[ENTITY_TYPE] = None, **kwargs) -> PaginateEntities:
        url_requested = EntityManager._get_url_filtered("%s%s" % (self.target_endpoint, requested_path), **kwargs)
        for element in self._paginate(url_requested, entity_type):
            yield element

    def _paginate(self, url_requested: str, entity_type: Optional[ENTITY_TYPE] = None) -> PaginateEntities:
        response = self.client.get(url_requested)
        while True:
            _logger.debug("GET - %s - %s", url_requested, response.text)
            response_json = self._read_response(response, JsonObject)
            for resource in response_json["resources"]:
                yield self._entity(resource, entity_type)
            if (
                    "next" not in response_json["pagination"]
                    or response_json["pagination"]["next"] is None
                    or response_json["pagination"]["next"].get("href") is None
            ):
                break
            else:
                url_requested = response_json["pagination"]["next"]["href"]
                response = self.client.get(url_requested)

    def _create(self, data: dict) -> Entity:
        url = "%s%s" % (self.target_endpoint, self.entity_uri)
        return self._post(url, data=data)

    def _upload_bits(self, resource_id: str, filename: str) -> Entity:
        url = "%s%s/%s/upload" % (self.target_endpoint, self.entity_uri, resource_id)
        files = {"bits": (filename, open(filename, "rb"))}
        return self._post(url, files=files)

    def _update(self, resource_id: str, data: dict) -> Entity:
        url = "%s%s/%s" % (self.target_endpoint, self.entity_uri, resource_id)
        return self._patch(url, data)

    def _remove(self, resource_id: str):
        url = "%s%s/%s" % (self.target_endpoint, self.entity_uri, resource_id)
        self._delete(url)

    def __iter__(self) -> PaginateEntities:
        return self.list()

    def __getitem__(self, entity_guid) -> Entity:
        return self.get(entity_guid)

    def list(self, **kwargs) -> PaginateEntities:
        return self._list(self.entity_uri, **kwargs)

    def get_first(self, **kwargs) -> Optional[Entity]:
        kwargs.setdefault("per_page", 1)
        for entity in self._list(self.entity_uri, **kwargs):
            return entity
        return None

    def get(self, entity_id: str, *extra_paths) -> Entity:
        if len(extra_paths) == 0:
            requested_path = "%s%s/%s" % (self.target_endpoint, self.entity_uri, entity_id)
        else:
            requested_path = "%s%s/%s/%s" % (self.target_endpoint, self.entity_uri, entity_id, "/".join(extra_paths))
        return self._get(requested_path)

    def _read_response(self, response: Response, entity_type: Optional[ENTITY_TYPE]) -> Union[JsonObject, Entity]:
        result = response.json(object_pairs_hook=JsonObject)
        if 'Location' in response.headers:
            result['links']['job'] = {
                "href": response.headers['Location'],
                "method": "GET",
            }

        return self._entity(result, entity_type)

    @staticmethod
    def _request(**mandatory_parameters) -> Request:
        return Request(**mandatory_parameters)

    def _entity(self, result: JsonObject, entity_type: Optional[ENTITY_TYPE]) -> Union[JsonObject, Entity]:
        if "guid" in result:
            return (entity_type or self.entity_type)(self.target_endpoint, self.client, **result)
        else:
            return result

    @staticmethod
    def _get_url_filtered(url: str, **kwargs) -> str:
        def _append_encoded_parameter(parameters: List[str], args: Tuple[str, Any]) -> List[str]:
            parameter_name, parameter_value = args[0], args[1]
            if isinstance(parameter_value, (list, tuple)):
                parameters.append("%s=%s" % (parameter_name, quote(",".join(parameter_value))))
            else:
                parameters.append("%s=%s" % (parameter_name, quote(str(parameter_value))))
            return parameters

        if len(kwargs) > 0:
            return "%s?%s" % (
                url, "&".join(functools.reduce(_append_encoded_parameter, sorted(list(kwargs.items())), [])))
        else:
            return url
