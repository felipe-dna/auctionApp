from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    itens = db.relationship('Item', backref='owner', lazy='dynamic')
    bids = db.relationship('Bid', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    initial_price = db.Column(db.Float)
    posted_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    expires_in = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bids = db.relationship('Bid', backref='bid_list', lazy='dynamic')

    def __repr__(self):
        return '<Item {}>'.format(self.name)


class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    value = db.Column(db.Integer)

    def __repr__(self):
        return '<Item {}>'.format(self.value)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))