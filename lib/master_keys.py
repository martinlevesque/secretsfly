import time
import copy
import os
from lib.log import logger

encrypted_master_keys = {}  # project_id -> { 'master_key': '...', 'set_at': 1234567890 }


def master_key_session_set(project):
    global encrypted_master_keys

    return encrypted_master_keys.get(str(project.id))


def delete_master_key(project_id):
    global encrypted_master_keys

    del encrypted_master_keys[str(project_id)]


def set_master_key(project_id, master_key):
    global encrypted_master_keys

    encrypted_master_keys[str(project_id)] = {
        'key': master_key,
        'set_at': int(time.time())
    }


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
