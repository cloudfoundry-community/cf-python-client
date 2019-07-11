import sys

if sys.version_info.major == 2:
    from mock import patch, call, MagicMock, mock_open
    from httplib import SEE_OTHER, CREATED, NO_CONTENT, ACCEPTED
    def iterate_text(text):
        for character in text:
            yield character
    built_in_entry = '__builtin__'

elif sys.version_info.major == 3:
    from unittest.mock import patch, call, MagicMock, mock_open
    from http import HTTPStatus
    SEE_OTHER = HTTPStatus.SEE_OTHER.value
    CREATED = HTTPStatus.CREATED.value
    NO_CONTENT = HTTPStatus.NO_CONTENT.value
    ACCEPTED = HTTPStatus.ACCEPTED.value
    def iterate_text(text):
        for character in text:
            yield bytes([character])
    built_in_entry = 'builtins'
else:
    raise ImportError('Invalid major version: %d' % sys.version_info.major)