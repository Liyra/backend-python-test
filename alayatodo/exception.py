from alayatodo import app
from flask import jsonify


class InvalidUsageJson(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsageJson)
def handle_invalid_todo_json(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response