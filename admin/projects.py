from flask import Blueprint, render_template, request
from db import Session
from models import Project

bp = Blueprint('admin_projects', __name__, url_prefix='/admin/projects/')

@bp.route('/', methods=['GET', 'POST'])
def index():
    session = Session()

    if request.method == 'POST':
        project = Project(**request.form)
        session.add(project)
        session.commit()

    projects = session.query(Project).all()

    return render_template('admin/projects/index.html', projects=projects, nb_projects=len(projects))

@bp.route('/new')
def new():
    return render_template('admin/projects/new.html')
