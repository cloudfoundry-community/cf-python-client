import sys

if sys.version_info.major == 2:
    from ConfigParser import ConfigParser, NoSectionError, NoOptionError
    from httplib import SEE_OTHER, CREATED, NO_CONTENT,HTTPConnection

elif sys.version_info.major == 3:
    from configparser import ConfigParser, NoSectionError, NoOptionError
    from http import HTTPStatus
    SEE_OTHER = HTTPStatus.SEE_OTHER.value
    CREATED = HTTPStatus.CREATED.value
    NO_CONTENT = HTTPStatus.NO_CONTENT.value
    from http.client import HTTPConnection
else:
    raise ImportError('Invalid major version: %d' % sys.version_info.major)