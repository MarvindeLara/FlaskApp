import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from program import db


class MyBadge(UserMixin, db.Model):
    __tablename__ = 'my_badges'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now, index=True)

    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    # player = db.relationship('Player', back_populates='my_badges')

    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    # badge = db.relationship('Badge', back_populates='my_badges')

