import base64
from sqlalchemy import Column, Integer, String
from models.common import *
from lib import encryption
from lib.log import logger
from db import session


class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, index=True, nullable=True)
    name = Column(String, nullable=False)
    description = Column(String)

    def is_root_project(self):
        # root projects have special features, such as having its own master key

        return not self.project_id

    def master_key_format_valid(master_key):
        return master_key and PROJECT_SERVICE_TOKEN_ENCODED_SEPARATOR not in master_key

    def prepare_master_key(master_key):
        result = master_key
        if not encryption.is_base64(master_key) or len(master_key) < encryption.KEY_LENGTH:
            if encryption.KEY_LENGTH - len(master_key) < encryption.KEY_LENGTH:
                missing_padding = encryption.KEY_LENGTH - len(master_key)
                result = base64.b64encode(
                    bytes(master_key + (encryption.KEY_PADDING * missing_padding), 'utf-8')
                ).decode('utf-8')

        return result

    def master_key_valid(self, master_key, first_project_secret):
        if not first_project_secret:
            return True

        try:
            first_project_secret.decrypt_latest_value(master_key)
        except Exception as e:
            logger.error(f"master key invalid for project {self.id}: {e}")
            return False

        return True

    def generate_master_key(self):
        if self.is_root_project():
            # new master key only for root projects
            return encryption.generate_key_b64()

    def parent_project(self):
        return session.query(Project).filter_by(id=self.project_id).first()
