import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from program import db


class MyPokemon(UserMixin, db.Model):
    __tablename__ = 'my_pokemons'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now, index=True)

    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    # player = db.relationship('Player', back_populates='my_pokemons')

    pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemons.id'), nullable=False)
    # pokemon = db.relationship('Pokemon', back_populates='my_pokemons')

