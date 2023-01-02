def assert_response_contains_html(content, response):
    assert content in response.data.decode()


def assert_response_does_not_contain_html(content, response):
    assert content not in response.data.decode()
