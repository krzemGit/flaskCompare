from comparator import db
from datetime import datetime

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