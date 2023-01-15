import time
from flask import Blueprint, render_template, request, redirect, url_for, g
from flask import session as http_session
from admin.session_util import master_key_session_set
from db import session
from models import Environment, Project, ServiceToken

bp = Blueprint('admin_secrets', __name__, url_prefix='/')


### Callbacks


### Endpoints


