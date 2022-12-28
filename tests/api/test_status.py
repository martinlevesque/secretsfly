

def test_api_status_endpoint(client):
    response = client.get('/api/status/')

    assert response.status_code == 200
    assert response.json == {'db': 'up'}

