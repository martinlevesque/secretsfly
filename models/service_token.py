from base64 import b64encode, b64decode
from sqlalchemy import create_engine, Column, event, DateTime, Integer, String, ForeignKey, text, func, and_, Index
from models.common import *
from models.project import Project
from models.environment import Environment
from sqlalchemy.orm import relationship
from lib import encryption
from db import session


class ServiceToken(Base):
    __tablename__ = 'service_tokens'

    environment = relationship('Environment', back_populates='service_tokens')

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey(Project.id), nullable=False)
    environment_id = Column(Integer, ForeignKey(Environment.id), nullable=False)
    friendly_name = Column(String)
    token = Column(String, index=True, nullable=False)  # sha-256 hash of the service token
    rights = Column(String, nullable=False, default=SERVICE_RIGHT_READ)  # comma-separated list of rights: read,write

    __table_args__ = (
        Index('idx_service_tokens_project_id_environment_id', project_id, environment_id),
    )

    def __str__(self):
        return f"ServiceToken(id={self.id}, project_id={self.project_id}, environment_id={self.environment_id}, " \
               f"friendly_name={self.friendly_name}, token=XXX, rights={self.rights})"

    def stringify_list_rights(input_rights):
        return ','.join(input_rights)

    def public_service_token(self, project_master_key):
        input_service_token = \
            bytes(f"{project_master_key}{PROJECT_SERVICE_TOKEN_ENCODED_SEPARATOR}{self.generated_token}", 'utf-8')
        return b64encode(input_service_token).decode('utf-8')

    def decode_public_service_token(pub_service_token):
        decoded_pub_service_token = b64decode(bytes(pub_service_token, 'utf-8')).decode('utf-8')
        parts = decoded_pub_service_token.split(PROJECT_SERVICE_TOKEN_ENCODED_SEPARATOR)

        if len(parts) != 2:
            raise Exception(f"Invalid public service token: {pub_service_token}")

        project_master_key = parts[0]
        b64_service_token = parts[1]

        stored_service_token = ServiceToken.hash_token(b64_service_token)

        service_token = session.query(ServiceToken).filter(ServiceToken.token == stored_service_token).first()

        if not service_token:
            raise Exception(f"Cannot find the service token: {pub_service_token}")

        return {
            'project_master_key': project_master_key,
            'service_token': service_token,
        }

    def hash_token(generated_token):
        return encryption.hash_string_sha256(generated_token)


@event.listens_for(ServiceToken, 'before_insert')
def populate_service_token_before_create(__mapper, __connection, target):
    target.generated_token = encryption.generate_key_b64()
    target.token = ServiceToken.hash_token(target.generated_token)
