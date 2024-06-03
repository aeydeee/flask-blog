# app/models.py
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from . import db


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    favorite_color = db.Column(db.String(120))
    about_author = db.Column(db.Text(120), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.now)
    profile_pic = db.Column(db.String(255), nullable=True)
    # Do some password stuff!
    password_hash = db.Column(db.String(128))
    # User Can have Many Posts!
    posts = db.relationship('Posts', backref='poster')

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.name}>'


# Create a Blog Post model
class Posts(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text())
    # author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.now)
    slug = db.Column(db.String(255))
    # Foreign Key to Link Users (refer to primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
