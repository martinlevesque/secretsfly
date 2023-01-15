import time
from flask import Blueprint, render_template, request, redirect, url_for, g
from flask import session as http_session
from admin.session_util import master_key_session_set
from db import session
from models import Environment, Project
from admin.service_tokens import bp as service_tokens_endpoints
from admin.secrets import bp as secrets_endpoints

bp = Blueprint('admin_projects', __name__, url_prefix='/projects/')

bp.register_blueprint(service_tokens_endpoints)
bp.register_blueprint(secrets_endpoints)


# Callbacks


@bp.before_request
def before_request_load_environment():
    environment_id = request.view_args.get('environment_id')

    if environment_id:
        g.environment = session.query(Environment).filter_by(id=environment_id).first()  # Load something by ID

@bp.before_request
def before_request_load_project():
    project_id = request.view_args.get('project_id')

    if project_id:
        g.project = session.query(Project).filter_by(id=project_id).first()  # Load something by ID


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

    projects = session.query(Project).all()

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

    http_session['projects_master_keys'] = http_session.get('projects_master_keys', {})
    http_session['projects_master_keys'][str(project.id)] = {
        'key': request.form[f"master_key_{project.id}"],
        'set_at': int(time.time())
    }

    return redirect(url_for('admin.admin_projects.get_project', project_id=project_id))


@bp.route('/new')
def new():
    return render_template('admin/projects/new.html')
