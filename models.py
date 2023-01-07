from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from lib import encryption
from base64 import b64encode

Base = declarative_base()

PROJECT_SERVICE_TOKEN_ENCODED_SEPARATOR = ':'


class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)

    def is_root_project(self):
        # root projects have special features, such as having its own master key

        return True

    def master_key_format_valid(master_key):
        return master_key and PROJECT_SERVICE_TOKEN_ENCODED_SEPARATOR not in master_key

    def generate_master_key(self):
        if self.is_root_project():
            # new master key only for root projects
            return encryption.generate_key_b64()


class Environment(Base):
    __tablename__ = 'environments'

    service_tokens = relationship('ServiceToken', back_populates='environment')

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


SERVICE_RIGHT_READ = 'read'
SERVICE_RIGHT_WRITE = 'write'


class ServiceToken(Base):
    __tablename__ = 'service_tokens'

    environment = relationship('Environment', back_populates='service_tokens')

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey(Project.id), nullable=False)
    environment_id = Column(Integer, ForeignKey(Environment.id), nullable=False)
    friendly_name = Column(String)
    token = Column(String, nullable=False)  # sha-256 hash of the service token
    rights = Column(String, nullable=False, default=SERVICE_RIGHT_READ)  # comma-separated list of rights: read,write

    def __str__(self):
        return f"ServiceToken(id={self.id}, project_id={self.project_id}, environment_id={self.environment_id}, " \
               f"friendly_name={self.friendly_name}, token=XXX, rights={self.rights})"

    def stringify_list_rights(input_rights):
        return ','.join(input_rights)

    def public_service_token(self, project_master_key):
        input_service_token = \
            bytes(f"{project_master_key}{PROJECT_SERVICE_TOKEN_ENCODED_SEPARATOR}{self.generated_token}", 'utf-8')
        return b64encode(input_service_token).decode('utf-8')

    def before_create(self):
        self.generated_token = encryption.generate_key_b64()
        self.token = encryption.hash_string_sha256(self.generated_token)

