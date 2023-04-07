from db import session
from tests import util

from models.environment import Environment
from models.secret import Secret, SecretValueHistory


from lib import encryption, master_keys
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

    # if we go to a different environment, we should see the secrets as importable

    diff_environment = session.query(Environment).filter(Environment.id != environment.id).first()
    response = client.get(f"/admin/projects/{project.id}/environments/{diff_environment.id}/secrets/")
    util.assert_response_contains_html('<legend>Missing secrets</legend>', response)
    util.assert_response_contains_html(f"{secret_payload['name']} (from environments: {environment.name})", response)


def test_admin_secrets_endpoint_disallow_without_master_key(client):
    # make a project
    project = helpers.make_project(client, "Test Project secrets - disallow without master key")
    master_keys.delete_master_key(project.id)

    environment = session.query(Environment).filter(Environment.id == 1).first()

    response = client.get(f"/admin/projects/{project.id}/environments/{environment.id}/secrets/")

    assert response.status_code == 302

def test_admin_secrets_with_parent_secrets_endpoint(client):
    master_key = encryption.generate_key_b64()
    # make a project
    project = helpers.make_project(client, "Test Project secrets test_admin_secrets_with_parent_secrets_endpoint",
                                   master_key=master_key)
    sub_project = helpers.make_project(
        client,
        "Test Project sub",
        master_key=master_key,
        parent_project_id=project.id
    )

    environment = session.query(Environment).filter(Environment.id == 1).first()

    helpers.make_secret(project, environment, {'name': 'test secret'}, secret_value='value1', master_key=master_key)
    helpers.make_secret(project, environment, {'name': 'secondsecret'}, secret_value='value2', master_key=master_key)
    helpers.make_secret(project, environment, {'name': 'thirdsecret'}, secret_value='value3', master_key=master_key)

    helpers.make_secret(sub_project, environment, {'name': 'thirdsecret'}, secret_value='value3updated',
                        master_key=master_key)

    response = client.get(f"/admin/projects/{sub_project.id}/environments/{environment.id}/secrets/?decrypt=true")

    assert response.status_code == 200
    util.assert_response_contains_html("Secrets for", response)
    util.assert_response_contains_html("test secret", response)
    util.assert_response_contains_html("'thirdsecret', `value3updated`", response)
    util.assert_response_contains_html("'secondsecret', `value2`", response)
    util.assert_response_contains_html("'test secret', `value1`", response)


def test_admin_secrets_endpoint_with_decryption(client):
    # make a project
    master_key = encryption.generate_key_b64()
    project = helpers.make_project(client, "Test Project secrets test_admin_secrets_endpoint_with_decryption",
                                   master_key)

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


def test_admin_create_secret_with_versioned_values_endpoint(client, monkeypatch):
    monkeypatch.setenv("VERSIONED_SECRET_VALUES", "false")

    # make a project
    master_key = encryption.generate_key_b64()
    project = helpers.make_project(client, "Test Project create secret "
                                           "test_admin_create_secret_with_versioned_values_endpoint",
                                   master_key)

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
                               f"secrets[{secret.id}][value]": "world"
                           })

    assert response.status_code == 200

    # get secret values
    secret_value_histories_cnt = session.query(SecretValueHistory).filter(SecretValueHistory.secret_id == secret.id).count()

    assert secret_value_histories_cnt == 1


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
