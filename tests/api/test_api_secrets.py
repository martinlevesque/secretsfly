import re
import json
from db import session

from models.environment import Environment
from models.service_token import ServiceToken

from lib import encryption
from tests.admin import helpers


def test_api_secrets_endpoint(client):
    # make a project
    master_key = encryption.generate_key_b64()
    project = helpers.make_project(client, "Test Project api secrets test_api_secrets_endpoint", master_key=master_key)
    sub_project = helpers.make_project(
        client,
        "Test Project sub test_api_secrets_endpoint",
        master_key=master_key,
        parent_project_id=project.id
    )
    environment = session.query(Environment).filter(Environment.id == 1).first()

    helpers.make_secret(project, environment, {'name': 'TEST_SECRET'}, secret_value='value1', master_key=master_key)
    helpers.make_secret(project, environment, {'name': 'secondsecret'}, secret_value='value2', master_key=master_key)
    helpers.make_secret(project, environment, {'name': 'thirdsecret'}, secret_value='value3', master_key=master_key)

    helpers.make_secret(sub_project, environment, {'name': 'thirdsecret'}, secret_value='value3updated',
                        master_key=master_key)

    response_service_token = helpers.make_service_token(client, sub_project, {
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

    assert json_response['secrets'][0]['name'] == 'thirdsecret'
    assert json_response['secrets'][0]['value'] == 'value3updated'
    assert json_response['secrets'][1]['name'] == 'secondsecret'
    assert json_response['secrets'][1]['value'] == 'value2'
    assert json_response['secrets'][2]['name'] == 'TEST_SECRET'
    assert json_response['secrets'][2]['value'] == 'value1'
