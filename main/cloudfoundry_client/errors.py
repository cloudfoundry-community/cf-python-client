import json
from http import HTTPStatus


class InvalidLogResponseException(Exception):
    pass


class InvalidStatusCode(Exception):
    def __init__(self, status_code: HTTPStatus, body):
        self.status_code = status_code
        self.body = body

    def __str__(self):
        if self.body is None:
            return self.status_code.name
        elif type(self.body) == str:
            return "%s : %s" % (self.status_code.name, self.body)
        else:
            return "%s : %s" % (self.status_code.name, json.dumps(self.body))


class InvalidEntity(Exception):
    def __init__(self, **kwargs):
        super(InvalidEntity, self).__init__()
        self.raw_entity = dict(**kwargs)

    def __str__(self):
        return "InvalidEntity: %s" % json.dumps(self.raw_entity)
