
from datetime import datetime
from base64 import b64encode, b64decode
from sqlalchemy import create_engine, Column, event, DateTime, Integer, String, ForeignKey, text, func, and_, Index
from sqlalchemy.orm import relationship
from lib import encryption
from db import session
from models.common import *
from models.project import Project
from models.environment import Environment

class Secret(Base):
    __tablename__ = 'secrets'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey(Project.id), nullable=False)
    environment_id = Column(Integer, ForeignKey(Environment.id), nullable=False)
    name = Column(String, nullable=False)
    comment = Column(String, nullable=False)
    secret_history_values = relationship('SecretValueHistory', back_populates='secret')

    loaded_project_master_key = None

    __table_args__ = (
        Index('idx_secrets_project_id_environment_id', project_id, environment_id),
    )

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

    def latest_value_histories(secret_ids):
        subquery = session.query(
            SecretValueHistory.secret_id,
            func.max(SecretValueHistory.id).label("max_id")
        ).filter(SecretValueHistory.secret_id.in_(secret_ids)) \
            .group_by(SecretValueHistory.secret_id).subquery()

        return session.query(SecretValueHistory).join(
            subquery,
            and_(
                SecretValueHistory.secret_id == subquery.c.secret_id,
                SecretValueHistory.id == subquery.c.max_id
            )
        ).all()

    def encrypt_value(project_master_key, decrypted_value):
        return encryption.encrypt(project_master_key, decrypted_value)

    def decrypt_latest_value(self, project_master_key):
        latest_history = self.latest_value_history()

        if not latest_history:
            return None

        return latest_history.decrypted_value(project_master_key)

    def decrypt_secrets(secrets, project_master_key):

        secret_ids = [secret.id for secret in secrets]

        secret_value_histories = Secret.latest_value_histories(secret_ids)
        secret_value_secret_id_hash = {
            secret_value_history.secret_id: secret_value_history
            for secret_value_history
            in secret_value_histories
        }

        for secret in secrets:
            latest_secret_history_value = secret_value_secret_id_hash.get(secret.id)

            if latest_secret_history_value:
                secret.value = latest_secret_history_value.decrypted_value(project_master_key)

    def retrieve_hierarchy_secrets(project_ids, environment_id=None):
        pre_filter = session.query(Secret) \
            .filter(Secret.project_id.in_(project_ids))

        if environment_id:
            pre_filter = pre_filter.filter_by(environment_id=environment_id)

        pre_filter = pre_filter.order_by(text('secrets.name DESC, secrets.id ASC'))

        result = pre_filter.all()

        # remove parent variable if child one is present
        elements_to_remove = []

        for index in range(len(result)):
            if index > 0 and result[index].name == result[index - 1].name:
                elements_to_remove.append(result[index - 1])

        for element in elements_to_remove:
            result.remove(element)

        return result

    def find_missing_secrets(project_ids, current_environment_id):
        cur_env_secrets = Secret.retrieve_hierarchy_secrets(project_ids, current_environment_id)

        # other environments where id different than current_environment_id:
        other_environments = session.query(Environment) \
            .filter(Environment.id != current_environment_id) \
            .all()

        missing_secrets = {}

        for environment in other_environments:
            other_env_secrets = Secret.retrieve_hierarchy_secrets(project_ids, environment.id)

            for secret in other_env_secrets:
                if secret.name not in [s.name for s in cur_env_secrets]:
                    if secret.name not in missing_secrets:
                        missing_secrets[secret.name] = {
                            'secret': secret,
                            'environments': [environment],
                            'environment_names': [environment.name],
                        }
                    else:
                        missing_secrets[secret.name]['environments'].append(environment)
                        missing_secrets[secret.name]['environment_names'].append(environment.name)

        return missing_secrets


@event.listens_for(Secret, 'before_insert')
def populate_secret_before_create(__mapper, __connection, target):
    if not target.comment:
        target.comment = ''


class SecretValueHistory(Base):
    __tablename__ = 'secret_value_histories'

    id = Column(Integer, primary_key=True)
    secret_id = Column(Integer, ForeignKey(Secret.id), index=True, nullable=False)
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

