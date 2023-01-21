import time
from flask import Blueprint, render_template, request, redirect, url_for, g
from flask import session as http_session
from admin.session_util import master_key_session_set, ensure_have_project_master_in_session
from db import session
from models import Environment, Project, Secret, SecretValueHistory

bp = Blueprint('admin_secrets', __name__, url_prefix='/')


### Callbacks


@bp.before_request
def before_request_ensure_have_project_master_in_session():
    g.with_decryption = request.args.get('decrypt') == 'true'
    g.requires_master_key = g.with_decryption

    if request.method == 'POST' or g.with_decryption:
        g.requires_master_key = True

        return ensure_have_project_master_in_session()


### Endpoints

SECRET_DEFAULT_VALUE = '--------'

@bp.route('/<project_id>/environments/<environment_id>/secrets/', methods=['GET', 'POST'])
def index(project_id, environment_id):
    if g.requires_master_key:
        project_master_key_info = master_key_session_set(g.project)
        g.project_master_key = project_master_key_info.get('key')

    if request.method == 'POST':

        def extract_secret_id(attribute_name, secret_name):
            begin_with = "secrets["
            ends_with = f"][{attribute_name}]"
            if begin_with in secret_name and ends_with in secret_name:
                return secret_name[secret_name.index(begin_with) + len(begin_with):secret_name.index(ends_with)]

        secrets = {}

        for variable_name, variable_value in request.form.items():
            if variable_value == SECRET_DEFAULT_VALUE:
                continue

            id_is = extract_secret_id('name', variable_name) or extract_secret_id('value', variable_name)

            if not secrets.get(id_is):
                secrets[id_is] = {}

            if '[name]' in variable_name:
                secrets[id_is]['name'] = variable_value

        for variable_id, variable in secrets.items():
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

    secrets = session.query(Secret) \
        .filter_by(project_id=project_id) \
        .filter_by(environment_id=environment_id) \
        .order_by(Secret.name.desc()).all()

    if g.with_decryption:
        secret_ids = [secret.id for secret in secrets]
        secret_latest_values_distinct_on_secret_id = session.query(SecretValueHistory) \
            .filter(SecretValueHistory.secret_id.in_(secret_ids)) \
            .order_by(SecretValueHistory.secret_id.desc(), SecretValueHistory.id.desc()).distinct(
            SecretValueHistory.secret_id).all()

        hash_secrets = {secret.id: secret for secret in secrets}
        for secret_value_history in secret_latest_values_distinct_on_secret_id:
            hash_secrets[secret_value_history.secret_id].value = secret_value_history.decrypt(
                g.project_master_key)
            print(hash_secrets[secret_value_history.secret_id].value)

    """
    from sqlalchemy.orm import subqueryload
session = create_session()
secrets = session.query(Secret).options(subqueryload(Secret.latest_secret_value_history)).all()
for secret in secrets:
    print(secret.latest_secret_value_history.id)
    """

    return render_template('admin/secrets/index.html',
                           project=g.project,
                           environment=g.environment,
                           secrets=secrets,
                           SECRET_DEFAULT_VALUE=SECRET_DEFAULT_VALUE)
