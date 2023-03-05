import time
from flask import Blueprint, render_template, request, redirect, url_for, g
from admin.session_util import master_key_session_set, ensure_have_project_master_in_session
from db import session
from models import Environment, Project, ServiceToken

bp = Blueprint('admin_service_tokens', __name__, url_prefix='/')


### Callbacks


@bp.before_request
def before_request_ensure_have_project_master_in_session():
    return ensure_have_project_master_in_session()


### Endpoints


@bp.route('/<project_id>/service-tokens/', methods=['GET', 'POST'])
def index(project_id):
    new_public_service_token = None

    if request.method == 'POST':
        service_token = ServiceToken(**request.form)
        service_token.project_id = project_id
        service_token.rights = ServiceToken.stringify_list_rights(request.form.getlist('rights'))

        session.add(service_token)
        session.commit()

        new_public_service_token = service_token.public_service_token(master_key_session_set(g.project).get('key'))

    # service tokens ordered by id desc with environment name
    service_tokens = session.query(ServiceToken) \
        .filter_by(project_id=project_id) \
        .join(Environment, ServiceToken.environment_id == Environment.id) \
        .order_by(ServiceToken.id.desc()).all()

    return render_template('admin/service_tokens/index.html',
                           project=g.project,
                           service_tokens=service_tokens,
                           new_public_service_token=new_public_service_token)


@bp.route('/<project_id>/service-tokens/<service_token_id>/destroy', methods=['POST'])
def destroy(project_id, service_token_id):
    service_token = session.query(ServiceToken).filter_by(id=service_token_id).first()
    session.delete(service_token)
    session.commit()

    return redirect(url_for('admin.admin_projects.admin_service_tokens.index', project_id=project_id))


@bp.route('/<project_id>/service-tokens/new', methods=['GET'])
def new(project_id):
    # available environment from db session:
    environments = session.query(Environment).all()
    return render_template('admin/service_tokens/new.html',
                           project=g.project,
                           environments=environments)
