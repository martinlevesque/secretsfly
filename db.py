import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

project_root = os.path.dirname(os.path.realpath(__file__))

db_env = 'current'

if os.environ.get('ENV'):
    db_env = os.environ.get('ENV')

DB_URL = f"sqlite:////{project_root}/db/self-secrets-manager-{db_env}.db"

engine = create_engine(DB_URL)

Session = sessionmaker(bind=engine)

session = scoped_session(Session)

