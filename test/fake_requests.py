from http import HTTPStatus
from json import loads
from unittest.mock import MagicMock


def iterate_text(text):
    for character in text:
        yield bytes([character])


class MockSession(object):
    def __init__(self):
        self.headers = dict()
        self.proxies = None
        self.verify = True
        self.trust_env = False


class MockResponse(object):
    def __init__(self, url: str, status_code: int, text: str, headers: dict = None):
        self.status_code = status_code
        self.url = url
        self.text = text
        self.headers = dict()
        self.is_redirect = status_code == HTTPStatus.SEE_OTHER
        if headers is not None:
            self.headers.update(headers)

    def check_data(self, data, json, **kwargs):
        pass

    def json(self, **kwargs):
        return loads(self.text, **kwargs)

    def __iter__(self):
        return iterate_text(self.text)


class FakeRequests(object):
    def __init__(self):
        self.Session = MagicMock()
        self.post = MagicMock()
        self.get = MagicMock()
        self.put = MagicMock()
        self.patch = MagicMock()
