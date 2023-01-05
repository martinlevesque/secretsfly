import re
import base64
from tests import util
from db import session
from models import ServiceToken, Project, PROJECT_SERVICE_TOKEN_ENCODED_SEPARATOR
from lib import encryption


def make_project(client, project_name, master_key):
    client.post('/admin/projects/', data={'name': project_name})

    project = session.query(Project).order_by(Project.id.desc()).first()

    client.post(f"/admin/projects/{project.id}/set-master-key",
                data={f"master_key_{project.id}": master_key})

    return project

def test_admin_service_tokens_endpoint(client):
    project = make_project(client, "Test Project 5", "my-master-key")
    response = client.get(f"/admin/projects/{project.id}/service-tokens/")

    assert response.status_code == 200
    util.assert_response_contains_html(f"Service Tokens for project Test Project 5", response)


def test_admin_service_tokens_new_endpoint(client):
    project = make_project(client, "Test Project 5", "my-master-key")
    response = client.get(f"/admin/projects/{project.id}/service-tokens/new")

    assert response.status_code == 200
    util.assert_response_contains_html(f"New Service Token", response)


def test_admin_create_service_token_endpoint(client):
    project = make_project(client, "Test Project create service token", "my-master-key")
    response = client.post(f"/admin/projects/{project.id}/service-tokens/",
                           data={
                               'friendly_name': 'ST 1',
                               'environment_id': 1,
                               'rights': 'read'
                           })

    assert response.status_code == 200
    util.assert_response_contains_html("service_token_input", response)
    content = response.data.decode()

    pattern = r'<input.+?id="service_token_input".+?value="(.+?)".+?>'
    match = re.search(pattern, content)

    assert match

    service_token = match.group(1)
    unbase64_service_token = base64.b64decode(bytes(service_token, 'utf-8')).decode('utf-8')

    assert PROJECT_SERVICE_TOKEN_ENCODED_SEPARATOR in unbase64_service_token
    parts = unbase64_service_token.split(PROJECT_SERVICE_TOKEN_ENCODED_SEPARATOR)

    assert len(parts) == 2
    assert parts[0] == "my-master-key"

    stored_service_token = encryption.hash_string_sha256(parts[1])

    # find the ServiceToken with token == stored_service_token
    db_service_token = session.query(ServiceToken).filter(ServiceToken.token == stored_service_token).first()

    assert db_service_token
    assert db_service_token.friendly_name == "ST 1"
    assert db_service_token.environment_id == 1
    assert db_service_token.project_id == project.id
    assert db_service_token.rights == "read"