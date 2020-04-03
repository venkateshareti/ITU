from flask import jsonify, Blueprint

errors = Blueprint('errors', __name__)


class CustomException(Exception):
    status_code = 500

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv, self.status_code


@errors.app_errorhandler(Exception)
def handle_error(error):

    message = [str(x) for x in error.args]
    try:
        status_code = error.__class__.code
    except Exception as e:
        status_code = 500
    response = {
        'success': False,
        'error': {
            'type': error.__class__.__name__,
            'message': message
        }
    }

    return jsonify(response), status_code
