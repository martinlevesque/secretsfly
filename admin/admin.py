import os
from flask import Blueprint, request
from admin.projects import bp as projects_endpoints
from lib import master_keys
from admin.auth import basic_auth

bp = Blueprint('admin', __name__, url_prefix='/admin/')
bp.register_blueprint(projects_endpoints)


@bp.before_request
@basic_auth.login_required
def before_request_admin():
    pass
