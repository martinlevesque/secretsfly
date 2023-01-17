import time
from flask import Blueprint, render_template, request, redirect, url_for, g
from flask import session as http_session
from admin.session_util import master_key_session_set
from db import session
from models import Environment, Project, Secret, SecretValueHistory

bp = Blueprint('admin_secrets', __name__, url_prefix='/')


### Callbacks


### Endpoints


@bp.route('/<project_id>/environments/<environment_id>/secrets/', methods=['GET', 'POST'])
def index(project_id, environment_id):
    if request.method == 'POST':
        print(f"should create")

    secrets = session.query(Secret) \
        .filter_by(project_id=project_id) \
        .filter_by(environment_id=environment_id) \
        .order_by(Secret.name.desc()).all()

    return render_template('admin/secrets/index.html',
                           project=g.project,
                           environment=g.environment,
                           secrets=secrets)
