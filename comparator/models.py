from comparator import db
from datetime import datetime, date

class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    username = db.Column(db.String(), default='guest')
    search_title = db.Column(db.String(), nullable=False)
    results = db.relationship('Result', backref='search', lazy=True)

    def __repr__(self):
        return f"Search('{self.id}', '{self.username}', '{self.phrases[0]}', '{self.search_date}')"

    def get_platforms(self):
        ''' method checks all platforms in the connected results '''
        platform_set = set()
        for result in self.results:
            platform_set.add(result.platform)
        platforms = [x for x in platform_set]
        platform_str = ', '.join(platforms)
        return platform_str

    def get_phrases(self):
        ''' method checks all phrases in the connected results '''
        phrase_set = set()
        for result in self.results:
            phrase_set.add(result.phrase)
        phrases = [x for x in phrase_set]
        phrase_str = ', '.join(phrases)
        return phrase_str


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_id = db.Column(db.Integer, db.ForeignKey('search.id'), nullable=False)
    phrase = db.Column(db.String(), nullable=False)
    platform = db.Column(db.String(), nullable=False)
    title = db.Column(db.String(), nullable=False)
    link = db.Column(db.String(), nullable=False)
    image = db.Column(db.String(), nullable=False)
    price_info = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f"Result('{self.id}', '{self.platform}', '{self.title}', '{self.price_info[0]}')"