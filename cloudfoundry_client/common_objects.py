import json
from collections.abc import Callable, Generator
from typing import TypeVar, Generic


class Request(dict):
    def __setitem__(self, key, value):
        if value is not None:
            super().__setitem__(key, value)


class JsonObject(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    json = json.dumps


ENTITY = TypeVar('ENTITY')


class Pagination(Generic[ENTITY], Generator[ENTITY, None, None]):
    def __init__(self, first_page: JsonObject,
                 total_result: int,
                 next_page_loader: Callable[[JsonObject], JsonObject | None],
                 resources_accessor: Callable[[JsonObject], list[JsonObject]],
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

    def send(self, value) -> ENTITY:
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

    def throw(self, typ, val=None, tb=None):
        super().throw(typ, val, tb)

    def close(self):
        super().close()

    def __iter__(self):
        return self

    def __next__(self) -> ENTITY:
        return self.send(None)
