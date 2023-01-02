import time
from freezegun import freeze_time
from datetime import datetime
from tests import util
from db import session
from models import Project
from flask import session as http_session


def test_admin_projects_endpoint(client):
    response = client.get('/admin/projects/')

    assert response.status_code == 200

    util.assert_response_contains_html('Projects (0)', response)


def test_admin_create_project_endpoint(client):
    response = client.post('/admin/projects/', data={'name': 'Test Project 2'})

    project = session.query(Project).order_by(Project.id.desc()).first()

    assert response.status_code == 200

    util.assert_response_contains_html('Projects (1)', response)
    util.assert_response_contains_html(f"<td>{project.id}</td>", response)
    util.assert_response_contains_html(f"<td>{project.name}</td>", response)
    util.assert_response_contains_html('New master key generated', response)


def test_admin_set_project_master_key_endpoint(client, monkeypatch):
    current_t = time.time()
    test_wait_duration = 5
    monkeypatch.setenv('ADMIN_MASTER_KEY_EXPIRATION', str(test_wait_duration))
    client.post('/admin/projects/', data={'name': 'Test Project 3'})
    new_project = session.query(Project).order_by(Project.id.desc()).first()

    response = client.post(f"/admin/projects/{new_project.id}/set-master-key",
                           data={f"master_key_{new_project.id}": 'my-master-key'})

    assert response.status_code == 302
    assert http_session['projects_master_keys'][str(new_project.id)]['key'] == 'my-master-key'

    response = client.get(f"/admin/projects/{new_project.id}")

    util.assert_response_does_not_contain_html("Project master key is not currently set", response)

    with freeze_time(datetime.fromtimestamp(current_t + test_wait_duration + 1)):
        response = client.get(f"/admin/projects/{new_project.id}")
        util.assert_response_contains_html("Project master key is not currently set", response)
