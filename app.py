from flask import Flask
from api.status import bp as status_endpoints
from admin.projects import bp as projects_endpoints
from lib import encryption
from db import session

app = Flask(__name__)

# app secret key is randomized at startup
app.secret_key = encryption.generate_key_b64()

# API
app.register_blueprint(status_endpoints)

# Admin
app.register_blueprint(projects_endpoints)


@app.teardown_request
def remove_session(ex=None):
    session.remove()
