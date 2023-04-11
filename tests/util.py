def assert_response_contains_html(content, response, occurrences=1):
    assert content in response.data.decode()

    if occurrences == 1:
        return

    count = response.data.decode().count(content)

    assert count == occurrences, f"Expected {occurrences} occurrences of '{content}', but found {count}."

def assert_response_does_not_contain_html(content, response):
    assert content not in response.data.decode()
