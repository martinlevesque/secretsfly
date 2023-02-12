import time
from flask import Blueprint, render_template, request, redirect, url_for, g
from sqlalchemy import text
from admin.session_util import master_key_session_set
from db import session
from models import Environment, Project
from admin.service_tokens import bp as service_tokens_endpoints
from admin.secrets import bp as secrets_endpoints
from lib import master_keys

bp = Blueprint('admin_projects', __name__, url_prefix='/projects/')

bp.register_blueprint(service_tokens_endpoints)
bp.register_blueprint(secrets_endpoints)


# Callbacks


@bp.before_request
def before_request_load_environment():
    environment_id = request.view_args.get('environment_id')

    if environment_id:
        g.environment = session.query(Environment).filter_by(id=environment_id).first()


@bp.before_request
def before_request_load_project():
    project_id = request.view_args.get('project_id')

    if project_id:
        g.project = session.query(Project).filter_by(id=project_id).first()


@bp.route('/', methods=['GET', 'POST'])
def index():
    new_master_key = None
    project = None

    if request.method == 'POST':
        project = Project(**request.form)

        session.add(project)
        session.commit()

        if project.is_root_project():
            new_master_key = project.generate_master_key()

    projects = session.query(Project)\
        .order_by(text('CASE WHEN project_id IS NULL THEN id ELSE project_id END, id'))\
        .all()

    return render_template('admin/projects/index.html',
                           project=project,
                           new_master_key=new_master_key,
                           projects=projects,
                           nb_projects=len(projects))


@bp.route('/<project_id>/', methods=['GET'])
def get_project(project_id):
    project = session.query(Project).filter_by(id=project_id).first()

    # retrieve all environments - environments could be specific to a project
    environments = session.query(Environment).all()

    return render_template('admin/projects/project.html',
                           project=project,
                           environments=environments,
                           nb_environments=len(environments),
                           project_master_key_is_set=master_key_session_set(project))


@bp.route('/<project_id>/set-master-key', methods=['POST'])
def set_project_master_key(project_id):
    project = session.query(Project).filter_by(id=project_id).first()

    master_key = request.form.get(f"master_key_{project.id}")

    if not Project.master_key_format_valid(master_key):
        return {"error": "Invalid master key format"}, 400

    master_keys.set_master_key(project.id, master_key)

    return redirect(url_for('admin.admin_projects.get_project', project_id=project_id))


@bp.route('/new')
def new():
    # retrieve all projects
    # without project_id, meaning it's a root project
    projects = session.query(Project).filter_by(project_id=None).all()
    return render_template('admin/projects/new.html', projects=projects)
