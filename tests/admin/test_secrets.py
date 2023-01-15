from db import session
from tests import util
from models import Environment, ServiceToken, Project, PROJECT_SERVICE_TOKEN_ENCODED_SEPARATOR
from lib import encryption
from tests.admin import helpers


def test_admin_secrets_endpoint(client):
    # make a project
    project = helpers.make_project(client, "Test Project secrets", "my-master-key")

    environment = session.query(Environment).filter(Environment.id == 1).first()

    secret_payload = {
        'name': 'test secret',

    }
    helpers.make_secret(project, environment, secret_payload)

    response = client.get(f"/admin/projects/{project.id}/environments/{environment.id}/secrets/")

    assert response.status_code == 200
    util.assert_response_contains_html(f"Secrets for", response)
    util.assert_response_contains_html(f"test secret", response)
