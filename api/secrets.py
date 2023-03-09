from flask import Blueprint, jsonify, request
from db import session
from models import Project, Secret, ServiceToken
from lib.log import logger
from functools import lru_cache
import time

bp = Blueprint('api_secrets', __name__, url_prefix='/api/secrets/')


@lru_cache
def get_service_token(header_service_token):
    decoded = ServiceToken.decode_public_service_token(header_service_token)
    project_master_key = decoded['project_master_key']
    service_token = decoded['service_token']

    return service_token, project_master_key


@bp.route('/')
def index():
    service_token = request.headers.get('authorization')

    service_token, project_master_key = get_service_token(service_token)

    project = session.query(Project).filter_by(id=service_token.project_id).first()

    secrets = Secret.retrieve_hierarchy_secrets(
        [service_token.project_id, project.project_id],
        service_token.environment_id
    )

    Secret.decrypt_secrets(secrets, project_master_key)

    json_secrets = []

    for s in secrets:
        s.loaded_project_master_key = project_master_key
        json_secrets.append(s.serialize)

    return jsonify(secrets=json_secrets)
