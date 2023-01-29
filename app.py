import os
from flask import Flask
from api.status import bp as status_endpoints
from admin.admin import bp as admin_endpoints
from lib import encryption
from models import Environment
from db import session, prepare_db

app = Flask(__name__)

app.debug = True

# app secret key is randomized at startup
app.secret_key = encryption.generate_key_b64()

# API
app.register_blueprint(status_endpoints)

# Admin
app.register_blueprint(admin_endpoints)

prepare_db()

# Initialize global environments

app.logger.debug('Initializing global environments')

AVAILABLE_ENVIRONMENTS = os.environ.get('AVAILABLE_ENVIRONMENTS', 'dev,staging,prod').split(',')

if not len(AVAILABLE_ENVIRONMENTS):
    raise Exception('No environments defined in AVAILABLE_ENVIRONMENTS')

for env in AVAILABLE_ENVIRONMENTS:
    # check if env exists in the database
    if not session.query(Environment).filter(Environment.name == env).first():
        # create env
        session.add(Environment(name=env))
        session.commit()

# end of global environments

@app.teardown_request
def remove_session(ex=None):
    session.remove()
