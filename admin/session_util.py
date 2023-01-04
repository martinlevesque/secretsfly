
from flask import session as http_session


def master_key_session_set(project):
    if http_session.get('projects_master_keys') and http_session['projects_master_keys'].get(str(project.id)):
        return http_session['projects_master_keys'][str(project.id)]
