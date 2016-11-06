import sys


if sys.version_info.major == 2:
    import mock
    from httplib import SEE_OTHER, CREATED, NO_CONTENT

elif sys.version_info.major == 3:
    from unittest import mock
    from http.client import SEE_OTHER, CREATED, NO_CONTENT

else:
    raise ImportError('Invalid major version: %d' % sys.version_info.major)