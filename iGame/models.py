from datetime import datetime
from sqlalchemy_serializer import SerializerMixin
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Column, Table, ForeignKey, Integer, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from . import login_manager


# association table created with Core, models created with ORM


class Base(DeclarativeBase):
    """
    sets some naming convention rules for future migrations in Alembic
    """
    metadata = MetaData(naming_convention={
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })


db = SQLAlchemy(model_class=Base)

#  changed to score to separate from IGDB "ratings" attribute
user_games = db.Table(
    'user_games',
    Column('user_id',db.ForeignKey('users.user_id'), primary_key=True),
    Column('game_id',db.ForeignKey('games.game_id'), primary_key=True),
    Column('likes', db.Boolean, nullable=False),
    Column('score', db.Integer, nullable=True)
)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id: Mapped[int] = mapped_column(db.Integer, primary_key=True, nullable=False)
    email_hash: Mapped[str] = mapped_column(db.String(32), nullable=False, default='')  # set:unique?
    created_on: Mapped[datetime] = mapped_column(db.DateTime(), default=datetime.now)

    # games: Mapped[list['Game']] = db.relationship(secondary=user_games, back_populates='users')

    def __init__(self, email):
        self.email_hash = email

    def __str__(self):
        return f"User Number {self.user_id}"


@login_manager.user_loader
def load_user(user_id):
    try:
        user = db.session.get(User, user_id)
    except:
        user = None
    return user


class Game(db.Model, SerializerMixin):
    """a table where USERID and GAMEID act as the primary key"""
    __tablename__ = 'games'
    game_id: Mapped[int] = mapped_column(db.Integer, primary_key=True, nullable=False)  # what are defaults here?
    title: Mapped[str] = mapped_column(db.String, nullable=False)  # need to index

    # users: Mapped[list['User']] = db.relationship(secondary=user_games, back_populates='games')

    def __init__(self, game_id, title):
        self.game_id = game_id
        self.title = title

    def __repr__(self):
        return f"UserGame: User {self.game_id}, Game {self.title}, Pref {self.users}"
