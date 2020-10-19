import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///saves.db'
# app.config['SECRET_KEY'] = 'konstantynopolitanczykowianeczka'
app.config.from_pyfile('./config/dev_env.cfg')
google_key = app.config['GOOGLE_APPLICATION_CREDENTIALS']
db = SQLAlchemy(app)

from comparator import routes_oop