import time
from flask import Blueprint, render_template, request, redirect, url_for
from flask import session as http_session
from admin.session_util import master_key_session_set
from db import session
from models import Project
from admin.service_tokens import bp as service_tokens_endpoints

bp = Blueprint('admin_projects', __name__, url_prefix='/projects/')

bp.register_blueprint(service_tokens_endpoints)


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

    return render_template('admin/projects/project.html',
                           project=project,
                           project_master_key_is_set=master_key_session_set(project))


@bp.route('/<project_id>/set-master-key', methods=['POST'])
def set_project_master_key(project_id):
    project = session.query(Project).filter_by(id=project_id).first()

    http_session['projects_master_keys'] = http_session.get('projects_master_keys', {})
    http_session['projects_master_keys'][str(project.id)] = {
        'key': request.form[f"master_key_{project.id}"],
        'set_at': int(time.time())
    }

    return redirect(url_for('admin.admin_projects.get_project', project_id=project_id))


@bp.route('/new')
def new():
    return render_template('admin/projects/new.html')

