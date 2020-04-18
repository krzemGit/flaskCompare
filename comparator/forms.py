from comparator import db
from wtforms import Form, BooleanField, StringField, validators

class First_search(Form):
    phrase = StringField('phrase', [validators.InputRequired()])
    amazon = BooleanField('amazon')
    ebay = BooleanField('ebay')
    allegro = BooleanField('allegro')