import time
from flask import Blueprint, render_template, request, redirect, url_for, g
from flask import session as http_session
from admin.session_util import master_key_session_set
from db import session
from models import Environment, Project, Secret, SecretValueHistory

bp = Blueprint('admin_secrets', __name__, url_prefix='/')

### Callbacks


### Endpoints

SECRET_DEFAULT_VALUE = '--------'


@bp.route('/<project_id>/environments/<environment_id>/secrets/', methods=['GET', 'POST'])
def index(project_id, environment_id):
    if request.method == 'POST':

        def extract_secret_id(attribute_name, secret_name):
            begin_with = "secrets["
            ends_with = f"][{attribute_name}]"
            if begin_with in secret_name and ends_with in secret_name:
                return secret_name[secret_name.index(begin_with) + len(begin_with):secret_name.index(ends_with)]

        secrets = {}

        for variable_name, variable_value in request.form.items():
            id_is = extract_secret_id('name', variable_name) or extract_secret_id('value', variable_name)

            if not secrets.get(id_is):
                secrets[id_is] = {}

            if '[name]' in variable_name:
                secrets[id_is]['name'] = variable_value

        for variable_id, variable in secrets.items():
            stripped_name = variable['name'].strip().upper()

            # find secret by project_id, environment_id and name
            secret = session.query(Secret) \
                .filter_by(project_id=project_id, environment_id=environment_id, name=stripped_name) \
                .first()

            if not secret:
                secret = Secret(project_id=project_id, environment_id=environment_id, name=stripped_name)

                session.add(secret)
                session.commit()

    secrets = session.query(Secret) \
        .filter_by(project_id=project_id) \
        .filter_by(environment_id=environment_id) \
        .order_by(Secret.name.desc()).all()

    return render_template('admin/secrets/index.html',
                           project=g.project,
                           environment=g.environment,
                           secrets=secrets,
                           SECRET_DEFAULT_VALUE=SECRET_DEFAULT_VALUE)
