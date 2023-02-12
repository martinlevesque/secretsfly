import re
import json
from db import session
from models import Environment, ServiceToken
from lib import encryption
from tests.admin import helpers


def test_api_secrets_endpoint(client):
    # make a project
    master_key = encryption.generate_key_b64()
    project = helpers.make_project(client, "Test Project api secrets", master_key=master_key)

    environment = session.query(Environment).filter(Environment.id == 1).first()

    secret_payload = {
        'name': 'TEST_SECRET'
    }
    secret = helpers.make_secret(
        project,
        environment,
        secret_payload,
        secret_value="hello secret",
        master_key=master_key
    )
    response_service_token = helpers.make_service_token(client, project, {
        'friendly_name': 'my service token api secrets',
        'environment_id': environment.id,
        'rights': 'read'
    })
    service_token_page = response_service_token.data.decode()
    pattern = r'<input.+?id="service_token_input".+?value="(.+?)".+?>'
    service_token = re.search(pattern, service_token_page)[1]

    response = client.get("/api/secrets/", headers={"Authorization": service_token})

    assert response.status_code == 200

    json_response = json.loads(response.data.decode())

    assert json_response['secrets'][0]['name'] == 'TEST_SECRET'
    assert json_response['secrets'][0]['value'] == 'hello secret'
