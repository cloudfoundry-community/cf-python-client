import logging
from cloudfoundry_client.v3.entities import EntityManager

_logger = logging.getLogger(__name__)


class PolicyManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(PolicyManager, self).__init__(target_endpoint, client, '/networking/v1/external/policies')

    def create(self, policies: list):
        """

        :param policies: the policies to create
        :type policies: list of dicts
        """
        return super(PolicyManager, self)._create({'policies': policies})

    def delete(self):
        pass