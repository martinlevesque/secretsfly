import time
import copy
import os
from threading import Thread
from lib.log import logger
from lib import encryption

base_master_key = encryption.generate_key_b64()
print(f"Base master key: {base_master_key}")
encrypted_master_keys = {}  # project_id -> { 'key': '...', 'set_at': 1234567890 }


def cron_check_master_keys_expiration():
    while True:
        check_for_expired_master_key()
        time.sleep(30)


def master_key_session_set(project):
    global encrypted_master_keys
    global base_master_key

    encrypted_master_key_info = copy.deepcopy(encrypted_master_keys.get(str(project.id)))

    if not encrypted_master_key_info:
        return None

    encrypted_master_key = encrypted_master_key_info.get('key')

    # just replace the original key object by the actual key
    encrypted_master_key_info['key'] = encryption.decrypt(
        base_master_key,
        encrypted_master_key['ciphered_data'],
        encrypted_master_key['iv']
    )

    return encrypted_master_key_info


def is_project_sealed(project):
    return master_key_session_set(project) is None


def delete_master_key(project_id):
    global encrypted_master_keys

    del encrypted_master_keys[str(project_id)]


def set_master_key(project_id, master_key):
    global encrypted_master_keys
    global base_master_key

    encrypted_master_key = encryption.encrypt(base_master_key, master_key)
    encrypted_master_keys[str(project_id)] = {
        'key': encrypted_master_key,
        'set_at': int(time.time())
    }

    return encrypted_master_key


def check_for_expired_master_key():
    global encrypted_master_keys

    mutated_master_keys = copy.deepcopy(encrypted_master_keys)
    changed = False

    for project_id, master_key in encrypted_master_keys.items():
        if not master_key.get('set_at'):
            continue

        time_diff = int(time.time()) - master_key['set_at']

        threshold_master_key_expiration = int(os.environ.get('ADMIN_MASTER_KEY_EXPIRATION', 300))

        if time_diff > threshold_master_key_expiration:
            logger.debug(f"Removing expired master key for project {project_id}")
            del mutated_master_keys[project_id]
            changed = True

    if changed:
        encrypted_master_keys = mutated_master_keys


if os.environ.get('ENV') != 'test':
    Thread(target=cron_check_master_keys_expiration).start()
