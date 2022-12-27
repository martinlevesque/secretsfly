from flask import Blueprint, render_template
from db import Session
from models import Project

bp = Blueprint('admin_projects', __name__, url_prefix='/admin/projects/')

@bp.route('/')
def index():
    projects = Session().query(Project).all()

    return render_template('admin/projects/index.html', projects=projects, nb_projects=len(projects))
