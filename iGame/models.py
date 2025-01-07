from datetime import datetime
from sqlalchemy_serializer import SerializerMixin
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from . import login_manager

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user_name = db.Column(db.String(50), nullable=False)  # encrypted email
    created_on = db.Column(db.DateTime(), default=datetime.now)

    def __init__(self, username: str):
        self.user_name = username


@login_manager.user_loader
def load_user(user_id):
    # TODO: wrap this in a try/except bc its contacting db ???
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


