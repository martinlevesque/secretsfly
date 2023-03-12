from sqlalchemy import Column, Integer, String
from models.common import *
from lib import encryption
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

    def generate_master_key(self):
        if self.is_root_project():
            # new master key only for root projects
            return encryption.generate_key_b64()

    def parent_project(self):
        return session.query(Project).filter_by(id=self.project_id).first()
