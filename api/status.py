from flask import Blueprint
from db import session
from models import Project
from lib.logging import logger

STATUS_UP = 'up'
STATUS_DOWN = 'down'

bp = Blueprint('api', __name__, url_prefix='/api/status/')


def sql_db_status():
    try:
        session.query(Project).count()
    except Exception as e:
        # todo replace by logger
        logger.error(f"SQL DB status error: {e}")
        return STATUS_DOWN

    return STATUS_UP

@bp.route('/')
def index():

    result = {
        'db': sql_db_status(),
    }

    status_code = 200 if list(set(list(result.values()))) == [STATUS_UP] else 500

    return result, status_code
