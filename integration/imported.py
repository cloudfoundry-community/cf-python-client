import sys


if sys.version_info.major == 2:
    from ConfigParser import ConfigParser, NoSectionError, NoOptionError
    from httplib import SEE_OTHER, CREATED, NO_CONTENT

elif sys.version_info.major == 3:
    from configparser import ConfigParser, NoSectionError, NoOptionError
    from http.client import SEE_OTHER, CREATED, NO_CONTENT

else:
    raise ImportError('Invalid major version: %d' % sys.version_info.major)