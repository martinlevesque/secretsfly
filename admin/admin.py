from flask import Blueprint, request
from admin.projects import bp as projects_endpoints
from lib import master_keys


bp = Blueprint('admin', __name__, url_prefix='/admin/')
bp.register_blueprint(projects_endpoints)


@bp.before_request
def check_expired_stored_master_keys():
    master_keys.check_for_expired_master_key()
