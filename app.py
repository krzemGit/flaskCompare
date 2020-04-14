from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, Markup
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, BooleanField, StringField, validators
from common import translate_to_polish, amazon_search, ebay_search, allegro_search, session_results, create_id

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///saves.db'
app.config['SECRET_KEY'] = 'konstantynopolitanczykowianeczka'

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
    search_id = db.Column(db.Integer)
    platform = db.Column(db.String(), nullable=False)
    title = db.Column(db.String(), nullable=False)
    link = db.Column(db.String(), nullable=False)
    image = db.Column(db.String(), nullable=False)
    price_info = db.Column(db.PickleType)

    def __repr__(self):
        return f"Result('{self.id}', '{self.platform}', '{self.title}', '{self.price_info[0]}')"

@app.route('/', methods=['POST','GET'])
def home():
    form = First_search()
    return render_template('home.html', form=form)

@app.route('/results/', methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        searches = Search.query.all()
        if len(searches) > 0:
            id = create_id(searches)
        else:
            id = 1
        name = request.form.get('your-name')
        submit_date = datetime.utcnow()
        search_title = request.form.get('search-title', 'no title')
        sphrase = session.get('sphrase', None)
        strans_phrase = session.get('stransphrase', None)
        sresults = session.get('sresults', None)
        res_no = len(sresults)
        phrase = f'<span id="phrase">{sphrase}</span><span class="trans-phrase"> (pol. {strans_phrase})</span>'
       
        db.session.add(Search(id=id , username=name , search_title=search_title , phrase=phrase))
        db.session.commit()

        for item in sresults:
            db.session.add(Result(search_id=id , platform=item['platform'] , title=item['title'] , link=item['link'] , image=item['image'] , price_info=list(item['price'])))
            db.session.commit()

        session.clear()

        return render_template('saved.html', submit_date=submit_date, title=search_title, phrase=phrase, res_no=res_no)

    elif request.method == 'GET':
        phrase = request.args.get('phrase')
        amazon = request.args.get('amazon')
        ebay = request.args.get('ebay')
        allegro = request.args.get('allegro')
        trans_phrase = translate_to_polish(phrase)
        results = []
        if amazon:
            results.extend(amazon_search(phrase))
        if ebay:
            results.extend(ebay_search(phrase))
        if allegro:
            results.extend(allegro_search(trans_phrase))
        session['sphrase'] = phrase
        session['stransphrase'] = trans_phrase
        session['sresults'] = session_results(results)
        return render_template('results.html', phrase=phrase, pol_phrase=trans_phrase, amazon=amazon, ebay=ebay, allegro=allegro, results=results)
    
if __name__ == "__main__":
    app.run(debug=True)

