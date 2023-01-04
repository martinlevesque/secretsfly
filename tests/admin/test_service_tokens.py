from tests import util
from db import session
from models import Project


def test_admin_service_tokens_endpoint(client):
    client.post('/admin/projects/', data={'name': 'Test Project 5'})

    project = session.query(Project).order_by(Project.id.desc()).first()

    client.post(f"/admin/projects/{project.id}/set-master-key",
                data={f"master_key_{project.id}": 'my-master-key'})

    response = client.get(f"/admin/projects/{project.id}/service-tokens/")

    assert response.status_code == 200
    util.assert_response_contains_html(f"Service Tokens for project Test Project 5", response)