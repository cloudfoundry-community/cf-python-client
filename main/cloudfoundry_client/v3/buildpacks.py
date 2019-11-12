from cloudfoundry_client.v3.entities import EntityManager


class BuildpackManager(EntityManager):
    def __init__(self, target_endpoint, client):
        super(BuildpackManager, self).__init__(target_endpoint, client, '/v3/buildpacks')

    def create(self, name, position=0, enabled=True, locked=False, stack=None,
               meta_labels=None, meta_annotations=None):
        # XXX typecheck? P3.7 => no problem, else it may be a little more code

        data = {
            'name': name,
            'position': position,
            'enabled': enabled,
            'locked': locked,
            'stack': stack,
            'metadata': {
                'labels': meta_labels,
                'annotations': meta_annotations
            }
        }
        return super(BuildpackManager, self)._create(data)

    def remove(self, buildpack_guid):
        super(BuildpackManager, self)._remove(buildpack_guid)

    # get and list are from main
    def update(self, buildpack_guid, name, position=0, enabled=True,
               locked=False, stack=None, meta_labels=None, meta_annotations=None):
        data = {
            'name': name,
            'position': position,
            'enabled': enabled,
            'locked': locked,
            'stack': stack,
            'metadata': {
                'labels': meta_labels,
                'annotations': meta_annotations
            }
        }
        return super(BuildpackManager, self)._update(buildpack_guid, data)

