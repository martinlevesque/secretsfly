
from models.common import *
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class Environment(Base):
    __tablename__ = 'environments'

    service_tokens = relationship('ServiceToken', back_populates='environment')

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
