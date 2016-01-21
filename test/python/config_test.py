import os
import ConfigParser
import logging

from cloudfoundry_client.client import CloudFoundryClient


_client = None
_org_guid = None
_space_guid = None
_app_guid = None


def _init_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)5s - %(name)s -  %(message)s')

def get_resource_dir():
    result = os.path.join(os.path.dirname(__file__), '..', 'resources')
    if not (os.path.exists(result) and os.path.isdir(result)):
        raise IOError('Directory %s must exist.' % result)
    return result


def get_resource(file_name):
    result = os.path.join(get_resource_dir(), file_name)
    if not (os.path.exists(result) and os.path.isfile(result) and os.access(result, os.R_OK)):
        raise IOError('File %s must exist.' % result)
    return result


def get_build_dir():
    result = os.path.join(os.path.dirname(__file__), '..', '..', 'dist')
    return result


def build_client_from_configuration():
    global _client
    if _client is None:
        _init_logging()
        cfg = ConfigParser.ConfigParser()
        cfg.read(get_resource('test.properties'))
        proxy = None
        try:
            http = cfg.get('proxy', 'http')
            https = cfg.get('proxy', 'https')
            proxy = dict(http=http, https=https)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError), _:
            pass
        skip_verification = False
        try:
            skip_verification_str = cfg.get('service', 'skip_ssl_verification')
            skip_verification = skip_verification_str.lower() == 'true'
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError), _:
            pass
        client = CloudFoundryClient(cfg.get('service', 'target_endpoint'), proxy=proxy,
                                    skip_verification=skip_verification)
        client.credentials_manager.init_with_credentials(cfg.get('authentification', 'login'),
                                                         cfg.get('authentification', 'password'))
        client.org_guid = cfg.get('test_data', 'org_guid')
        client.space_guid = cfg.get('test_data', 'space_guid')
        client.app_guid = cfg.get('test_data', 'app_guid')
        client.log_app_guid = cfg.get('test_data', 'log_app_guid')
        client.service_guid = cfg.get('test_data', 'service_guid')
        client.service_name = cfg.get('test_data', 'service_name')
        client.plan_guid = cfg.get('test_data', 'plan_guid')
        client.creation_parameters = eval(cfg.get('test_data', 'creation_parameters'))
        client.update_parameters = eval(cfg.get('test_data', 'update_parameters'))
        _client = client

    return _client
