from flask import Blueprint, render_template, request, redirect, url_for
from flask import session as http_session
from db import session
from models import Project

bp = Blueprint('admin_projects', __name__, url_prefix='/admin/projects/')

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


@bp.route('/<project_id>', methods=['GET'])
def get_project(project_id):
    project = session.query(Project).filter_by(id=project_id).first()

    return render_template('admin/projects/project.html',
                           project=project,
                           project_master_key_is_set=master_key_session_set(project))


@bp.route('/<project_id>/set-master-key', methods=['POST'])
def set_project_master_key(project_id):
    project = session.query(Project).filter_by(id=project_id).first()

    http_session[f"project_master_key_{project.id}"] = request.form[f"master_key_{project.id}"]

    return redirect(url_for('admin_projects.get_project', project_id=project_id))


@bp.route('/new')
def new():
    return render_template('admin/projects/new.html')


def master_key_session_set(project):
    return http_session.get(f"project_master_key_{project.id}") is not None
