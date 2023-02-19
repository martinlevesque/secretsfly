import time
from freezegun import freeze_time
from datetime import datetime
from tests import util
from db import session
from models import Environment, Project
from tests.admin import helpers
from lib import master_keys
from lib import encryption


def test_admin_projects_endpoint(client):
    response = client.get('/admin/projects/')

    assert response.status_code == 200

    util.assert_response_contains_html('Projects (0)', response)


def test_admin_projects_endpoint_with_many(client):
    # generate master ket
    master_key = encryption.generate_key_b64()
    project_1 = helpers.make_project(client, "project endpoint 1", master_key=master_key)
    response = client.post(f"/admin/projects/{project_1.id}/set-master-key",
                           data={f"master_key_{project_1.id}": master_key})
    assert response.status_code == 302
    helpers.make_project(client, "project endpoint 2")

    response = client.get('/admin/projects/')

    assert response.status_code == 200

    util.assert_response_contains_html('Projects (2)', response)
    assert response.data.count(b'[unsealed]') == 1


def test_admin_create_project_endpoint(client):
    # delete all projects
    session.query(Project).delete()

    response = client.post('/admin/projects/', data={'name': 'Test Project 2'})

    project = session.query(Project).order_by(Project.id.desc()).first()

    assert response.status_code == 200

    util.assert_response_contains_html('Projects (1)', response)
    util.assert_response_contains_html(f"<td>{project.id}</td>", response)
    util.assert_response_contains_html(f"{project.name}", response)
    util.assert_response_contains_html('New master key generated', response)


def test_admin_set_project_master_key_endpoint(client, monkeypatch):
    with freeze_time("2015-01-01 12:05:30"):
        test_wait_duration = 5
        monkeypatch.setenv('ADMIN_MASTER_KEY_EXPIRATION', str(test_wait_duration))
        client.post('/admin/projects/', data={'name': 'Test Project 3'})
        new_project = session.query(Project).order_by(Project.id.desc()).first()

        response = client.post(f"/admin/projects/{new_project.id}/set-master-key",
                               data={f"master_key_{new_project.id}": 'my-master-key'})

        assert response.status_code == 302
        assert master_keys.master_key_session_set(new_project)['key'] == 'my-master-key'

        response = client.get(f"/admin/projects/{new_project.id}/")

        util.assert_response_does_not_contain_html("Project master key is not currently set", response)

        # all environments should be listed in the project page
        environments = session.query(Environment).all()

        for environment in environments:
            util.assert_response_contains_html(environment.name, response)


def test_admin_seal_project_master_key_endpoint(client, monkeypatch):
    client.post('/admin/projects/', data={'name': 'Test Project seal'})
    new_project = session.query(Project).order_by(Project.id.desc()).first()

    client.post(f"/admin/projects/{new_project.id}/set-master-key",
                data={f"master_key_{new_project.id}": 'my-master-key'})

    assert not master_keys.is_project_sealed(new_project)

    response = client.get(f"/admin/projects/{new_project.id}/seal")

    util.assert_response_does_not_contain_html("Master key has been sealed successfully", response)

    assert master_keys.is_project_sealed(new_project)


def test_admin_set_project_master_key_with_invalid_master_key(client, monkeypatch):
    test_wait_duration = 5
    monkeypatch.setenv('ADMIN_MASTER_KEY_EXPIRATION', str(test_wait_duration))
    client.post('/admin/projects/', data={'name': 'Test Project inv master key'})
    new_project = session.query(Project).order_by(Project.id.desc()).first()

    response = client.post(f"/admin/projects/{new_project.id}/set-master-key",
                           data={f"master_key_{new_project.id}": 'mymasterkey:invalid'})

    assert response.status_code == 400
