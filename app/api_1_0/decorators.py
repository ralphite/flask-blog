__author__ = 'yawen'

from functools import wraps
from flask import g
from .authentication import forbidden


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden('Permission denied')
            return f(*args, **kwargs)
        return decorated_function
    return decorator