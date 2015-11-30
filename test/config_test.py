import os
import ConfigParser

from cloudfoundry.client import CloudFoundryClient

_client = None

def build_client_from_configuration():
    global _client
    if _client is None:
        path = os.path.join(os.path.dirname(__file__), 'test.properties')
        if not(os.path.exists(path) and os.path.isfile(path) and os.access(path, os.R_OK)):
            raise IOError('File %s must exist. Please use provided template')
        cfg = ConfigParser.ConfigParser()
        cfg.read(path)
        proxy = None
        try:
            http = cfg.get('proxy', 'http')
            https = cfg.get('proxy', 'https')
            proxy = dict(http=http, https=https)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError),_:
            pass
        skip_verification = False
        try:
            skip_verification_str =cfg.get('service', 'skip_ssl_verification')
            skip_verification = skip_verification_str.lower() == 'true'
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError), _:
            pass
        client = CloudFoundryClient(cfg.get('service', 'target_endpoint'), proxy=proxy,
                                    skip_verification=skip_verification)
        client.credentials_manager.init_with_credentials(cfg.get('authentification', 'login'),
                                                         cfg.get('authentification', 'password'))
        _client = client
    return _client
