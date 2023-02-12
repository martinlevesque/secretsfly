import time
import os
from flask import Blueprint, render_template, request, redirect, url_for, g, jsonify
from sqlalchemy import text
from admin.session_util import master_key_session_set, ensure_have_project_master_in_session
from db import session
from models import Environment, Project, Secret, SecretValueHistory

bp = Blueprint('admin_secrets', __name__, url_prefix='/')


### Callbacks


@bp.before_request
def before_request_ensure_have_project_master_in_session():
    g.with_decryption = request.args.get('decrypt') == 'true'
    g.requires_master_key = g.with_decryption

    if request.method in ['POST', 'DELETE'] or g.with_decryption:
        g.requires_master_key = True

        return ensure_have_project_master_in_session()


@bp.before_request
def before_request_check_format():
    g.format = 'json' if request.args.get('format') == 'json' else 'html'


### Endpoints

SECRET_DEFAULT_VALUE = '--------'
NB_MINUTES_DECRYPTED_BEFORE_REDIRECT = int(os.environ.get('NB_MINUTES_DECRYPTED_BEFORE_REDIRECT', 5))


def load_master_key():
    if g.requires_master_key:
        project_master_key_info = master_key_session_set(g.project)
        g.project_master_key = project_master_key_info.get('key')


@bp.route('/<project_id>/environments/<environment_id>/secrets/', methods=['GET', 'POST'])
def index(project_id, environment_id):
    load_master_key()

    if request.method == 'POST':
        secrets = secrets_from_form(request.form)
        upsert_secrets(project_id, environment_id, secrets)

    # filter by if project_id or g.project.project_id
    secrets = Secret.retrieve_hierarchy_secrets([project_id, g.project.project_id], environment_id)

    all_secrets = session.query(Secret) \
        .all()

    for s in all_secrets:
        print(f"secret: {s}")

    if g.with_decryption:
        Secret.decrypt_secrets(secrets, g.project_master_key)

    if g.format == 'json':
        json_secrets = []
        for s in secrets:
            s.loaded_project_master_key = g.project_master_key
            json_secrets.append(s.serialize)
        return jsonify(secrets=json_secrets)

    return render_template('admin/secrets/index.html',
                           project=g.project,
                           environment=g.environment,
                           secrets=secrets,
                           with_decryption=g.with_decryption,
                           SECRET_DEFAULT_VALUE=SECRET_DEFAULT_VALUE,
                           NB_MINUTES_DECRYPTED_BEFORE_REDIRECT=NB_MINUTES_DECRYPTED_BEFORE_REDIRECT)


@bp.route('/<project_id>/environments/<environment_id>/secrets/<secret_id>/destroy/', methods=['POST'])
def given_secret(project_id, environment_id, secret_id):
    load_master_key()

    secret = session.query(Secret) \
        .filter_by(project_id=project_id) \
        .filter_by(environment_id=environment_id) \
        .filter_by(id=secret_id) \
        .one()

    Secret.decrypt_secrets([secret], g.project_master_key)

    secret_values = session.query(SecretValueHistory) \
        .filter_by(secret_id=secret_id) \
        .all()

    for secret_value in secret_values:
        session.delete(secret_value)

    session.delete(secret)
    session.commit()

    return redirect(url_for('admin.admin_projects.admin_secrets.index',
                            project_id=project_id,
                            environment_id=environment_id))


def extract_secret_id(attribute_name, secret_name):
    begin_with = "secrets["
    ends_with = f"][{attribute_name}]"

    if begin_with in secret_name and ends_with in secret_name:
        return secret_name[secret_name.index(begin_with) + len(begin_with):secret_name.index(ends_with)]


def secrets_from_form(form_variables):
    secrets = {}

    for variable_name, variable_value in form_variables.items():
        if variable_value == SECRET_DEFAULT_VALUE:
            continue

        id_is = extract_secret_id('name', variable_name) or extract_secret_id('value', variable_name)

        if not secrets.get(id_is):
            secrets[id_is] = {}

        if '[name]' in variable_name:
            secrets[id_is]['name'] = variable_value

        if '[value]' in variable_name:
            secrets[id_is]['value'] = variable_value

    return secrets


def upsert_secrets(project_id, environment_id, secrets):
    for variable_id, variable in secrets.items():
        variable_value = variable.get('value')

        if not variable_value:
            continue

        stripped_name = variable['name'].strip().upper()

        # find secret by project_id, environment_id and name
        secret = None

        if 'new' not in variable_id:
            secret = session.query(Secret).filter_by(
                project_id=project_id,
                environment_id=environment_id,
                id=int(variable_id)) \
                .first()

        if not secret:
            secret = Secret(project_id=project_id, environment_id=environment_id, name=stripped_name)

            session.add(secret)
            session.commit()

        latest_secret_history_value = session.query(SecretValueHistory) \
            .filter_by(secret_id=secret.id) \
            .order_by(SecretValueHistory.id.desc()) \
            .first()

        if not latest_secret_history_value or \
                latest_secret_history_value.decrypted_value(g.project_master_key) != variable_value:
            # insert new secret value history
            encrypted_value_info = Secret.encrypt_value(g.project_master_key, variable_value)

            secret_value_history = SecretValueHistory(
                secret_id=secret.id,
                encrypted_value=encrypted_value_info['ciphered_data'],
                iv_value=encrypted_value_info['iv'],
                comment='')
            session.add(secret_value_history)
            session.commit()
