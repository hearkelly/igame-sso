from datetime import datetime

from sqlalchemy.orm import relationship, backref
from sqlalchemy_serializer import SerializerMixin
from flask_sqlalchemy import SQLAlchemy
from functions import hash_pass
from flask_login import UserMixin
from . import login_manager

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user_name = db.Column(db.String(50), nullable=False)
    pass_hash = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.now)

    def __init__(self, username: str, password: str, email: str):
        self.user_name = username
        self.password = password
        self.email = email

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.pass_hash = hash_pass(password)

    def verify_password(self, password):
        return self.pass_hash == hash_pass(password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# for the bag ('liked' games)
class Game(db.Model, SerializerMixin):
    """a table where USERID and GAMEID act as the primary key"""
    __tablename__ = "games"
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), primary_key=True, nullable=False)
    game_id = db.Column(db.Integer(), primary_key=True, nullable=False)
    likes = db.Column(db.Boolean(), nullable=False)
    rating = db.Column(db.Integer(), nullable=True)  # currently used for QA only

    def __init__(self, user, game, pref):
        self.user_id = user
        self.game_id = game
        self.likes = pref

    def __repr__(self):
        return f'UserGame: User {self.user_id}, Game {self.game_id}, Pref {self.likes}'


