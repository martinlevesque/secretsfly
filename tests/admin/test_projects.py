from tests import util
from db import Session
from models import Project

def test_admin_projects_endpoint(client):
    response = client.get('/admin/projects/')

    assert response.status_code == 200

    util.assert_response_contains_html('Projects (0)', response)


def test_admin_create_project_endpoint(client):
    response = client.post('/admin/projects/', data={'name': 'Test Project 2'})

    project = Session().query(Project).order_by(Project.id.desc()).first()

    assert response.status_code == 200

    util.assert_response_contains_html('Projects (1)', response)
    util.assert_response_contains_html(f"<td>{project.id}</td>", response)
    util.assert_response_contains_html(f"<td>{project.name}</td>", response)
