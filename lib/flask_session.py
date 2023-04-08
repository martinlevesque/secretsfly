#
# flask_session: provides a way  to store session data about which user has access to which projects based on the provided master keys.
#


from flask import session as flask_session


def add_project_access(project_id):
    flask_session['projects_access'] = list(set(flask_session.get('projects_access', []) + [int(project_id)]))


def remove_project_access(project_id):
    flask_session['projects_access'] = list(set(flask_session.get('projects_access', [])) - {int(project_id)})


def get_projects_access():
    return flask_session.get('projects_access', [])