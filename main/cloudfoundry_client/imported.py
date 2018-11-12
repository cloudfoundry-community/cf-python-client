import sys

import requests

if sys.version_info.major == 2:

    from httplib import UNAUTHORIZED, BAD_REQUEST, NOT_FOUND, OK
    from urllib import quote
    from urlparse import urlparse

    requests.packages.urllib3.disable_warnings()
    from __builtin__ import reduce

    def bufferize_string(content):
        return content
elif sys.version_info.major == 3:
    from http import HTTPStatus
    UNAUTHORIZED = HTTPStatus.UNAUTHORIZED.value
    BAD_REQUEST = HTTPStatus.BAD_REQUEST.value
    NOT_FOUND = HTTPStatus.NOT_FOUND.value
    OK = HTTPStatus.OK.value
    from urllib.parse import quote, urlparse
    from functools import reduce

    def bufferize_string(content):
        return bytes(content, 'UTF-8')

else:
    raise ImportError('Invalid major version: %d' % sys.version_info.major)
