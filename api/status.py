from flask import Blueprint

bp = Blueprint('api', __name__, url_prefix='/api/status/')

@bp.route('/')
def index():
    test = 'Hello World!'
    print(f"hello!")
    return {}

@bp.route('/another')
def another():
    return 'Hello, World 2!'