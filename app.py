from flask import Flask
from api.status import bp as status_bp

app = Flask(__name__)

app.register_blueprint(status_bp)
