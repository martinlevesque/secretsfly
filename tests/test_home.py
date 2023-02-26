from tests import util


def test_homepage(client):
    response = client.get('/')

    assert response.status_code == 200

    util.assert_response_contains_html('Welcome to', response)
