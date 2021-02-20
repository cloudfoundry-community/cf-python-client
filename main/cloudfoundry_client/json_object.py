import json


class JsonObject(dict):
    def __init__(self, *args, **kwargs):
        super(JsonObject, self).__init__(*args, **kwargs)

    json = json.dumps
