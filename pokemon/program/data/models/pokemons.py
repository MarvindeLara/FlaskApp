import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from program import db
from program.data.models.my_pokemons import MyPokemon


class Pokemon(UserMixin, db.Model):
    __tablename__ = 'pokemons'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now, index=True)
    name = db.Column(db.String(80), index=True, nullable=False)
    types = db.Column(db.String(80), index=True, nullable=False)
    abilities = db.Column(db.String(120), index=True, nullable=False)
    img_url = db.Column(db.String(120), index=True, nullable=False)
    coins = db.Column(db.Integer, default=0, index=True, nullable=False)

    my_pokemons = db.relationship('MyPokemon', order_by=[MyPokemon.created_date.desc()], backref='pokemon')

    def __repr__(self):
        return 'Pokemon {}'.format(self.name)

