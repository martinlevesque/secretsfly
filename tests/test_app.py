import app
from models.environment import Environment
from db import session


def test_app_initializing_default_global_environments():
    # get the environment "prod" from the Environment model
    env = session.query(Environment).filter(Environment.name == 'production').first()
    assert env
