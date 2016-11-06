import sys

import requests

if sys.version_info.major == 2:

    from httplib import UNAUTHORIZED, BAD_REQUEST, NOT_FOUND, OK
    from urllib import quote

    requests.packages.urllib3.disable_warnings()
    from __builtin__ import reduce

    def bufferize_string(content):
        return content
elif sys.version_info.major == 3:
    from http.client import UNAUTHORIZED, BAD_REQUEST, NOT_FOUND, OK
    from urllib.parse import quote
    from functools import reduce

    def bufferize_string(content):
        return bytes(content, 'UTF-8')

else:
    raise ImportError('Invalid major version: %d' % sys.version_info.major)
