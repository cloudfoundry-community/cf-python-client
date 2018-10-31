import sys

if sys.version_info.major == 2:
    from mock import patch, call, MagicMock
    from httplib import SEE_OTHER, CREATED, NO_CONTENT
    def iterate_text(text):
        for character in text:
            yield character

elif sys.version_info.major == 3:
    from unittest.mock import patch, call, MagicMock
    from http.client import SEE_OTHER, CREATED, NO_CONTENT
    def iterate_text(text):
        for character in text:
            yield bytes([character])
else:
    raise ImportError('Invalid major version: %d' % sys.version_info.major)