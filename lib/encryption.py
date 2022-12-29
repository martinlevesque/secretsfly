
from Crypto.Random import get_random_bytes
import binascii

def generate_key_s():
    # AES 256 bits
    return binascii.hexlify(get_random_bytes(32)).decode()

def key_s_to_bytes(key_s):
    return binascii.unhexlify(key_s)

