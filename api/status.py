from flask import Blueprint
from db import Session
from models import Project

bp = Blueprint('api', __name__, url_prefix='/api/status/')

def sql_db_status():
    try:
        session = Session()
        session.query(Project).count()
    except Exception as e:
        # todo replace by logger
        print(f"Exception: {e}")
        return 'down'

    return 'up'

@bp.route('/')
def index():

    return {
        'db': sql_db_status(),
    }
