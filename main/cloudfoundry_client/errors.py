import json
from http import HTTPStatus


class InvalidLogResponseException(Exception):
    pass


class InvalidStatusCode(Exception):
    def __init__(self, status_code: HTTPStatus, body, request_id=None):
        self.status_code = status_code
        self.body = body
        self.request_id = request_id

    def __str__(self):
        error_message = self.status_code.name
        if type(self.body) == str:
            error_message += f" = {self.body}"
        else:
            error_message += f" = {json.dumps(self.body)}"
        if self.request_id:
            error_message += f" - vcap-request-id = {self.request_id}"
        return error_message


class InvalidEntity(Exception):
    def __init__(self, **kwargs):
        super(InvalidEntity, self).__init__()
        self.raw_entity = dict(**kwargs)

    def __str__(self):
        return "InvalidEntity: %s" % json.dumps(self.raw_entity)
