from flask import g, request, redirect, url_for
from models import ServiceToken
from lib import master_keys
from admin.auth import basic_auth


def master_key_session_set(project):
    service_token = request.headers.get('authorization')

    if service_token and not basic_auth.admin_is_authenticated():
        # find service token in db using service_token
        decoded = ServiceToken.decode_public_service_token(service_token)

        return {'key': decoded['project_master_key']}

    return master_keys.master_key_session_set(project)


def ensure_have_project_master_in_session():
    if not master_key_session_set(g.project):
        return redirect(url_for('admin.admin_projects.get_project', project_id=g.project.id))
