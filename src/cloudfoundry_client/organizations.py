from cloudfoundry_client.entities import EntityManager
from urllib import quote


class OrganizationManager(EntityManager):
    def __init__(self, target_endpoint, credentials_manager):
        super(OrganizationManager, self).__init__(target_endpoint, credentials_manager)

    def list(self):
        for resource in super(OrganizationManager, self)._list('%s/v2/organizations' % self.target_endpoint):
            yield resource
            import logging

            logging.error(resource['entity']['name'])

    def get_by_id(self, organization_guid):
        return super(OrganizationManager, self)._get_one('%s/v2/organizations/%s' % (self.target_endpoint,
                                                                                     organization_guid))

    def get_by_name(self, name):
        query = quote('name:%s' % name)
        return super(OrganizationManager, self)._get_first('%s/v2/organizations?q=%s' % (self.target_endpoint,
                                                                                       query))