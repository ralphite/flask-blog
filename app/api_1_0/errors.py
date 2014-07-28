__author__ = 'yawen'

from flask import jsonify
from ..models import ValidationError
from . import api


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


def unauthorized(message):
    return forbidden(message)


def bad_request(message):
    return forbidden(message)


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])