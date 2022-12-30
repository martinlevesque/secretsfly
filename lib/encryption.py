from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode


def generate_key_b64():
    # AES 256 bits
    orig_key = get_random_bytes(32)
    return b64encode(orig_key).decode('utf-8')


def b64_to_bytes(b64_str):
    return b64decode(b64_str)


def encrypt(private_key_s, str_to_encrypt):
    cipher = AES.new(b64_to_bytes(private_key_s), AES.MODE_CBC)
    ciphered_data = cipher.encrypt(pad(bytes(str_to_encrypt, 'utf-8'), AES.block_size))

    return {
        'ciphered_data': b64encode(ciphered_data).decode('utf-8'),
        'iv': b64encode(cipher.iv).decode('utf-8')
    }


def decrypt(private_key_s, ciphered_data, iv_s):
    cipher = AES.new(b64_to_bytes(private_key_s), AES.MODE_CBC, b64decode(iv_s))

    return unpad(cipher.decrypt(b64_to_bytes(ciphered_data)), AES.block_size).decode()
