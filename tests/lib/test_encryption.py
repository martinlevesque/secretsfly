
from lib import encryption

def test_encryption_is_base64_valid_base64_string():
    assert encryption.is_base64("YmFzZTY0IGVuY29kZWQgc3RyaW5n") == True

def test_encryption_is_base64_invalid_base64_string():
    assert encryption.is_base64("hello world") == False

def test_encryption_is_base64_empty_string():
    assert encryption.is_base64("") == False