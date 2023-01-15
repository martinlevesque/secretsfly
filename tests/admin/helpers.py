
from models import Environment, ServiceToken, Project, Secret
from db import session

def make_project(client, project_name, master_key):
    response = client.post('/admin/projects/', data={'name': project_name})

    assert response.status_code == 200

    project = session.query(Project).order_by(Project.id.desc()).first()

    client.post(f"/admin/projects/{project.id}/set-master-key",
                data={f"master_key_{project.id}": master_key})

    return project


def make_service_token(client, project, payload):
    return client.post(f"/admin/projects/{project.id}/service-tokens/", data=payload)

def make_secret(project, environment, payload):
    payload['project_id'] = project.id
    payload['environment_id'] = environment.id

    payload['comment'] = payload.get('comment', '')

    secret = Secret(**payload)
    session.add(secret)
    session.commit()

    return secret

