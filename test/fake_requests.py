import os
from http import HTTPStatus
from json import loads
from typing import Optional
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
    def __init__(self, url: str, status_code: HTTPStatus, text: str, headers: dict = None):
        self.status_code = status_code.value
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


TARGET_ENDPOINT = "http://somewhere.org"


def get_fixtures_path(*paths):
    return os.path.join(os.path.dirname(__file__), 'fixtures', *paths)


def mock_response(uri: str, status_code: HTTPStatus, headers: Optional[dict], *path_parts: str):
    global TARGET_ENDPOINT
    if len(path_parts) > 0:
        file_name = path_parts[len(path_parts) - 1]
        extension_idx = file_name.rfind('.')
        binary_file = extension_idx >= 0 and file_name[extension_idx:] == '.bin'
        with(open(get_fixtures_path(*path_parts),
                  'rb' if binary_file else 'r')) as f:
            return MockResponse(url='%s%s' % (TARGET_ENDPOINT, uri),
                                status_code=status_code,
                                text=f.read(),
                                headers=headers)
    else:
        return MockResponse('%s%s' % (TARGET_ENDPOINT, uri),
                            status_code,
                            '')


class FakeRequests(object):
    def __init__(self):
        self.Session = MagicMock()
        self.post = MagicMock()
        self.get = MagicMock()
        self.put = MagicMock()
        self.patch = MagicMock()
