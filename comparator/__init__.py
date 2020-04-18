from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///saves.db'
app.config['SECRET_KEY'] = 'konstantynopolitanczykowianeczka'
db = SQLAlchemy(app)


from comparator import routes