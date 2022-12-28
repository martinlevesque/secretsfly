
def assert_response_contains_html(content, response):
    assert content in response.data.decode()