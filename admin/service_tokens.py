import time
from flask import Blueprint, render_template, request, redirect, url_for
from flask import session as http_session
from db import session
from models import Project

bp = Blueprint('admin_service_tokens', __name__, url_prefix='/')


@bp.route('/<project_id>/service-tokens', methods=['GET', 'POST'])
def index(project_id):
    project = session.query(Project).filter_by(id=project_id).first()

    return render_template('admin/service_tokens/index.html',
                           project=project)
