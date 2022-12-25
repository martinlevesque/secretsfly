import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

project_root = os.path.dirname(os.path.realpath(__file__))
DB_URL = f"sqlite:////{project_root}/db/self-secrets-manager-current.db"

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

