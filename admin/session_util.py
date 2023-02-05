from flask import session as http_session, g, request, redirect, url_for
from models import ServiceToken


def master_key_session_set(project):
    service_token = request.headers.get('authorization')

    if service_token:
        # find service token in db using service_token
        decoded = ServiceToken.decode_public_service_token(service_token)

        return {'key': decoded['project_master_key']}

    if http_session.get('projects_master_keys') and http_session['projects_master_keys'].get(str(project.id)):
        return http_session['projects_master_keys'][str(project.id)]


def ensure_have_project_master_in_session():
    if not master_key_session_set(g.project):
        return redirect(url_for('admin.admin_projects.get_project', project_id=g.project.id))
