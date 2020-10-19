import re
from comparator import db
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField
from wtforms.validators import Length, DataRequired

class First_search(FlaskForm):
    phrase = StringField('phrase', validators=[DataRequired(), Length(min=3, max=20)])
    amazon = BooleanField('amazon')
    ebay = BooleanField('ebay')
    allegro = BooleanField('allegro')

class New_search(FlaskForm):
    username = StringField('Username', validators=[Length(min=3, max=20)])
    search_title = StringField('Search title', validators=[DataRequired(), Length(min=3, max=30)])
