from lib import encryption

TEST_PRIVATE_KEY = "o4JIvbjOHQPEvlXIXyROjnG6+WlcFhdij0W7ctUGiLg="


def test_encryption_is_base64_valid_base64_string():
    assert encryption.is_base64("YmFzZTY0IGVuY29kZWQgc3RyaW5n") == True


def test_encryption_is_base64_invalid_base64_string():
    assert encryption.is_base64("hello world") == False


def test_encryption_is_base64_empty_string():
    assert encryption.is_base64("") == False


def test_encryption_generate_key_b64():
    key = encryption.generate_key_b64()
    assert encryption.is_base64(key) == True
    assert len(key) == 44


def test_encryption_encrypt():
    result = encryption.encrypt(TEST_PRIVATE_KEY, "hello world")

    assert len(result['ciphered_data']) > 10
    assert len(result['iv']) > 10


def test_encryption_decrypt():
    encryption_result = {'ciphered_data': 'jeGgcvgU3cwDSyAfjmwd+w==', 'iv': 'uhse6c2xnoSG9mjI2EQnEg=='}

    result = encryption.decrypt(TEST_PRIVATE_KEY, encryption_result['ciphered_data'], encryption_result['iv'])
    assert result == "hello world"
