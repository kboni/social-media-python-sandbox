import os
import flask_restful
from flask import Flask, g
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

api = flask_restful.Api(app)

db = SQLAlchemy(app)

basic_auth = HTTPBasicAuth()
