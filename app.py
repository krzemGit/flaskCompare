from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, BooleanField, StringField, validators
from common import translate_to_polish, amazon_search, ebay_search, allegro_search

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///saves.db'

db = SQLAlchemy(app)

# search form
class First_search(Form):
    phrase = StringField('phrase', [validators.InputRequired()])
    amazon = BooleanField('amazon')
    ebay = BooleanField('ebay')
    allegro = BooleanField('allegro')

# search and results register class

class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    username = db.Column(db.String(), nullable=False)
    search_title = db.Column(db.String())
    phrase = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f"Search('{self.id}', '{self.username}', '{self.phrase}', '{self.search_date}')"



class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(), nullable=False)
    title = db.Column(db.String(), nullable=False)
    link = db.Column(db.String(), nullable=False)
    image = db.Column(db.String(), nullable=False)
    price_info = db.Column(db.PickleType)

    def __repr__(self):
        return f"Result('{self.id}', '{self.platform}', '{self.title}', '{self.price_info[1]}')"

@app.route('/', methods=['POST','GET'])
def home():
    form = First_search()
    return render_template('home.html', form=form)

@app.route('/results/', methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        # TODO get data from the form (use session for transferring data)
        # use resutls use iterating over values of a dict, each value a separate list of object, only objects go to database
    elif request.method == 'GET':
        phrase = request.args.get('phrase')
        amazon = request.args.get('amazon')
        ebay = request.args.get('ebay')
        allegro = request.args.get('allegro')
        trans_phrase = translate_to_polish(phrase)
        # dictionary of JSON lists
        results = {}
        if amazon:
            results['amazon'] = amazon_search(phrase)
        if ebay:
            results['ebay'] = ebay_search(phrase)
        if allegro:
            results['allegro'] = allegro_search(trans_phrase)
        session['sphrase'] = phrase
        session['stransphrase'] = trans_phrase
        session['sresults'] = results
        return render_template('results.html', phrase=phrase, pol_phrase=trans_phrase, amazon=amazon, ebay=ebay, allegro=allegro, results=results)
    
if __name__ == "__main__":
    app.run(debug=True)

