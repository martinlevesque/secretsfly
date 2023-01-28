from db import session
from tests import util
from models import Environment, Secret, ServiceToken, Project, PROJECT_SERVICE_TOKEN_ENCODED_SEPARATOR
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


def test_admin_secrets_endpoint_with_decryption(client):
    # make a project
    master_key = encryption.generate_key_b64()
    project = helpers.make_project(client, "Test Project secrets", master_key)

    environment = session.query(Environment).filter(Environment.id == 1).first()

    secret_payload = {
        'name': 'TEST_SECRET'
    }
    helpers.make_secret(
        project,
        environment,
        secret_payload,
        secret_value="hello secret",
        master_key=master_key
    )

    response = client.get(f"/admin/projects/{project.id}/environments/{environment.id}/secrets/?decrypt=true")

    assert response.status_code == 200
    util.assert_response_contains_html("Secrets for", response)
    util.assert_response_contains_html("TEST_SECRET", response)
    util.assert_response_contains_html("hello secret", response)


def test_admin_create_secret_endpoint(client):
    # make a project
    master_key = encryption.generate_key_b64()
    project = helpers.make_project(client, "Test Project create secret", master_key)

    environment = session.query(Environment).filter(Environment.id == 1).first()

    secret_payload = {
        'name': 'TEST_SECRET2'
    }
    secret = helpers.make_secret(
        project,
        environment,
        secret_payload,
        secret_value="hello",
        master_key=master_key
    )

    response = client.post(f"/admin/projects/{project.id}/environments/{environment.id}/secrets/",
                           data={
                               f"secrets[{secret.id}][name]": "TEST_SECRET2",
                               f"secrets[{secret.id}][value]": "world",
                               f"secrets[new-0][name]": "TEST_SECRET3",
                               f"secrets[new-0][value]": "sec3",
                               f"secrets[new-1][name]": "TEST_SECRET4",
                               f"secrets[new-1][value]": "sec4",
                           })

    assert response.status_code == 200

    secret = session.query(Secret).filter(Secret.name == "TEST_SECRET2").first()
    assert secret.decrypt_latest_value(master_key) == "world"
    secret = session.query(Secret).filter(Secret.name == "TEST_SECRET3").first()
    assert secret.decrypt_latest_value(master_key) == "sec3"
    secret = session.query(Secret).filter(Secret.name == "TEST_SECRET4").first()
    assert secret.decrypt_latest_value(master_key) == "sec4"


def test_admin_delete_secret_endpoint(client):
    # make a project
    project = helpers.make_project(client, "Test Project secrets delete", "my-master-key")

    environment = session.query(Environment).filter(Environment.id == 1).first()

    secret_payload = {
        'name': 'test secret123',
    }
    secret = helpers.make_secret(project, environment, secret_payload)

    response = client.post(f"/admin/projects/{project.id}/environments/{environment.id}/secrets/{secret.id}/destroy/")
    assert response.status_code == 302

    response = client.get(f"/admin/projects/{project.id}/environments/{environment.id}/secrets/")

    assert response.status_code == 200
    util.assert_response_contains_html(f"Secrets for", response)
    util.assert_response_does_not_contain_html(f"test secret123", response)
