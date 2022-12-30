from flask import Blueprint, render_template, request
from db import Session
from models import Project

bp = Blueprint('admin_projects', __name__, url_prefix='/admin/projects/')

@bp.route('/', methods=['GET', 'POST'])
def index():
    session = Session()
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

@bp.route('/new')
def new():
    return render_template('admin/projects/new.html')
