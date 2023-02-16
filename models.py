from datetime import datetime
from base64 import b64encode, b64decode
from sqlalchemy import create_engine, Column, event, DateTime, Integer, String, ForeignKey, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from lib import encryption
from db import session

Base = declarative_base()

PROJECT_SERVICE_TOKEN_ENCODED_SEPARATOR = ':'


class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, nullable=True)
    name = Column(String, nullable=False)
    description = Column(String)

    def is_root_project(self):
        # root projects have special features, such as having its own master key

        return not self.project_id

    def master_key_format_valid(master_key):
        return master_key and PROJECT_SERVICE_TOKEN_ENCODED_SEPARATOR not in master_key

    def generate_master_key(self):
        if self.is_root_project():
            # new master key only for root projects
            return encryption.generate_key_b64()

    def parent_project(self):
        return session.query(Project).filter_by(id=self.project_id).first()


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


class Secret(Base):
    __tablename__ = 'secrets'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey(Project.id), nullable=False)
    environment_id = Column(Integer, ForeignKey(Environment.id), nullable=False)
    name = Column(String, nullable=False)
    comment = Column(String, nullable=False)
    secret_history_values = relationship('SecretValueHistory', back_populates='secret')

    loaded_project_master_key = None

    def __str__(self):
        return f"Secret(id={self.id}, project_id={self.project_id}, environment_id={self.environment_id}, " \
               f"name={self.name}, comment={self.comment}, value=XXX)"


    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'value': self.decrypt_latest_value(self.loaded_project_master_key)
        }

    def latest_value_history(self):
        # latest SecretValueHistory by secret_id
        return session.query(SecretValueHistory) \
            .filter_by(secret_id=self.id) \
            .order_by(SecretValueHistory.id.desc()) \
            .first()

    def encrypt_value(project_master_key, decrypted_value):
        return encryption.encrypt(project_master_key, decrypted_value)

    def decrypt_latest_value(self, project_master_key):
        return self.latest_value_history().decrypted_value(project_master_key)

    def decrypt_secrets(secrets, project_master_key):
        for secret in secrets:
            latest_secret_history_value = secret.latest_value_history()

            if latest_secret_history_value:
                secret.value = latest_secret_history_value.decrypted_value(project_master_key)

    def retrieve_hierarchy_secrets(project_ids, environment_id):
        result = session.query(Secret) \
            .filter(Secret.project_id.in_(project_ids)) \
            .filter_by(environment_id=environment_id) \
            .order_by(text('secrets.name DESC, secrets.id ASC')).all()

        # remove parent variable if child one is present
        elements_to_remove = []

        for index in range(len(result)):
            if index > 0 and result[index].name == result[index - 1].name:
                elements_to_remove.append(result[index - 1])

        for element in elements_to_remove:
            result.remove(element)

        return result


@event.listens_for(Secret, 'before_insert')
def populate_secret_before_create(__mapper, __connection, target):
    if not target.comment:
        target.comment = ''


class SecretValueHistory(Base):
    __tablename__ = 'secret_value_histories'

    id = Column(Integer, primary_key=True)
    secret_id = Column(Integer, ForeignKey(Secret.id), nullable=False)
    encrypted_value = Column(String, nullable=False)
    iv_value = Column(String, nullable=False)
    comment = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    secret = relationship('Secret', back_populates='secret_history_values')

    value = None

    def decrypt(self, project_master_key):
        self.value = self.decrypted_value(project_master_key)

        return self.value

    def decrypted_value(self, project_master_key):
        return encryption.decrypt(project_master_key, self.encrypted_value, self.iv_value)


@event.listens_for(SecretValueHistory, 'before_update')
def populate_secret_value_history_updated_at(mapper, connection, target):
    target.updated_at = datetime.utcnow()
