import copy
import os
import time
from flask import Blueprint, request
from flask import session as http_session
from admin.projects import bp as projects_endpoints
from lib.logging import logger


bp = Blueprint('admin', __name__, url_prefix='/admin/')
bp.register_blueprint(projects_endpoints)


@bp.before_request
def check_expired_stored_master_keys():
    mutated_projects_master_keys = {}
    changed = False

    for project_id, master_key in http_session.get('projects_master_keys', {}).items():
        if not master_key.get('set_at'):
            continue

        mutated_projects_master_keys[str(project_id)] = copy.deepcopy(master_key)

        time_diff = int(time.time()) - master_key['set_at']

        threshold_master_key_expiration = int(os.environ.get('ADMIN_MASTER_KEY_EXPIRATION', 300))

        if time_diff > threshold_master_key_expiration:
            logger.debug(f"Removing expired master key for project {project_id}")
            del mutated_projects_master_keys[str(project_id)]
            changed = True

    if changed:
        http_session['projects_master_keys'] = mutated_projects_master_keys



