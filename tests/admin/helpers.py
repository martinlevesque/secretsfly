from models import Environment, ServiceToken, Project, Secret, SecretValueHistory
from db import session


def make_project(client, project_name, master_key=None, parent_project_id=None):
    project_payload = {
        'name': project_name,
        'project_id': parent_project_id
    }
    response = client.post('/admin/projects/', data=project_payload)

    assert response.status_code == 200

    project = session.query(Project).order_by(Project.id.desc()).first()

    if master_key:
        client.post(f"/admin/projects/{project.id}/set-master-key",
                    data={f"master_key_{project.id}": master_key})

    return project


def make_service_token(client, project, payload):
    return client.post(f"/admin/projects/{project.id}/service-tokens/", data=payload)


def make_secret(project, environment, payload, secret_value=None, master_key=None):
    payload['project_id'] = project.id
    payload['environment_id'] = environment.id

    payload['comment'] = payload.get('comment', '')

    secret = Secret(**payload)
    session.add(secret)
    session.commit()

    if secret_value:
        encrypted_value_info = Secret.encrypt_value(master_key, secret_value)

        secret_value_history = SecretValueHistory(
            secret_id=secret.id,
            encrypted_value=encrypted_value_info['ciphered_data'],
            iv_value=encrypted_value_info['iv'],
            comment='')
        session.add(secret_value_history)
        session.commit()

    return secret


def first_environment(id=None):
    if id is None:
        id = 1

    return session.query(Environment).filter_by(id=id).first()
