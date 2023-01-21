
from flask import session as http_session, g, redirect, url_for


def master_key_session_set(project):
    if http_session.get('projects_master_keys') and http_session['projects_master_keys'].get(str(project.id)):
        return http_session['projects_master_keys'][str(project.id)]


def ensure_have_project_master_in_session():
    if not master_key_session_set(g.project):
        return redirect(url_for('admin.admin_projects.get_project', project_id=g.project.id))
