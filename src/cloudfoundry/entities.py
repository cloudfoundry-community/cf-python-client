class EntityManager(object):
    def __init__(self, target_endpoint, credentials_manager):
        self.target_endpoint = target_endpoint
        self.credentials_manager = credentials_manager