import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from program import db
from program.data.models.my_badges import MyBadge
from program.data.models.my_pokemons import MyPokemon


class Player(UserMixin, db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now, index=True)
    last_login = db.Column(db.DateTime, default=datetime.datetime.now, index=True)
    full_name = db.Column(db.String(80), index=True, nullable=True)
    email = db.Column(db.String(80), index=True, unique=True, nullable=False)
    hashed_password = db.Column(db.String(120), index=True, unique=False, nullable=False)
    coins = db.Column(db.Integer, default=0, index=True, unique=False, nullable=False)
    earned = db.Column(db.Integer, default=0, index=True, unique=False, nullable=True)

    my_pokemons = db.relationship('MyPokemon', order_by=[MyPokemon.created_date.desc()], backref='player')
    my_badges = db.relationship('MyBadge', order_by=[MyBadge.created_date.desc()], backref='player')

    def __repr__(self):
        return 'Player {}'.format(self.full_name)

