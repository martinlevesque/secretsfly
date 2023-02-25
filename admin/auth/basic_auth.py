import os
from functools import wraps
from flask import request, Response


def check_auth(username, password):
    return username == os.environ.get('ADMIN_BASIC_AUTH_USERNAME') and \
        password == os.environ.get('ADMIN_BASIC_AUTH_PASSWORD')


def authenticate():
    return Response(
        'Unauthorized',
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization

        if os.environ.get('ADMIN_BASIC_AUTH_USERNAME'):
            if not auth or not check_auth(auth.username, auth.password):
                return authenticate()

        return f(*args, **kwargs)

    return decorated_function
