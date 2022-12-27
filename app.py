from flask import Flask
from api.status import bp as status_endpoints
from admin.projects import bp as projects_endpoints

app = Flask(__name__)

# API
app.register_blueprint(status_endpoints)

# Admin
app.register_blueprint(projects_endpoints)
