import os
from json import loads

from imported import SEE_OTHER, iterate_text, MagicMock


class MockSession(object):
    def __init__(self):
        self.headers = dict()
        self.proxies = None
        self.verify = True
        self.trust_env = False


class MockResponse(object):
    def __init__(self, url, status_code, text, headers=None):
        self.status_code = status_code
        self.url = url
        self.text = text
        self.headers = dict()
        self.is_redirect = status_code == SEE_OTHER
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


def mock_response(uri, status_code, headers, *path_parts):
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
