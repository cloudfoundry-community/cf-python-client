import json
from typing import Callable, TypeVar, Generic, List, Optional


class Request(dict):
    def __setitem__(self, key, value):
        if value is not None:
            super(Request, self).__setitem__(key, value)


class JsonObject(dict):
    def __init__(self, *args, **kwargs):
        super(JsonObject, self).__init__(*args, **kwargs)

    json = json.dumps


ENTITY = TypeVar('ENTITY')


class Pagination(Generic[ENTITY]):
    def __init__(self, first_page: JsonObject,
                 total_result: int,
                 next_page_loader: Callable[[JsonObject], Optional[JsonObject]],
                 resources_accessor: Callable[[JsonObject], List[JsonObject]],
                 instance_creator: Callable[[JsonObject], ENTITY]):
        self._first_page = first_page
        self._total_results = total_result
        self._next_page_loader = next_page_loader
        self._resources_accessor = resources_accessor
        self._instance_creator = instance_creator
        self._cursor = None
        self._current_page = None

    @property
    def total_results(self) -> int:
        return self._total_results

    def __iter__(self):
        return self

    def __next__(self) -> ENTITY:
        try:
            if self._cursor is None:
                self._current_page = self._first_page
                self._cursor = self._resources_accessor(self._current_page).__iter__()
            return self._instance_creator(self._cursor.__next__())
        except StopIteration:
            self._current_page = self._next_page_loader(self._current_page)
            if self._current_page is None:
                raise
            self._cursor = self._resources_accessor(self._current_page).__iter__()
            return self._instance_creator(self._cursor.__next__())
