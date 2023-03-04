import os
import time
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

project_root = os.path.dirname(os.path.realpath(__file__))

db_env = 'current'

if os.environ.get('ENV'):
    db_env = os.environ.get('ENV')

db_location = f"{project_root}/db/"
default_db_folder = db_location

if os.environ.get('DB_FOLDER'):
    db_location = os.environ.get('DB_FOLDER')

db_path = f"{db_location}secretsfly-{db_env}.db"


def prepare_db():
    print(f"Initalizing with database with DB located at {db_path}")

    if not Path(db_path).is_file():
        src_file = f"{default_db_folder}secretsfly-current.db"
        dest_file = db_path
        print(f"Initializing database... from {src_file} to {dest_file}")
        os.system(f"cp {src_file} {dest_file}")
        os.system(f"ls -la {db_location}")
        time.sleep(3)


DB_URL = f"sqlite:///{db_path}"

engine = create_engine(DB_URL)

Session = sessionmaker(bind=engine)

session = scoped_session(Session)
