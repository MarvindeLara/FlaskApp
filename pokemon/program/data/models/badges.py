import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from program import db
from program.data.models.my_badges import MyBadge


class Badge(UserMixin, db.Model):
    __tablename__ = 'badges'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.now, index=True)
    name = db.Column(db.String(80), index=True, nullable=False)
    file_name = db.Column(db.String(80), index=True, nullable=False)
    description = db.Column(db.String(240), index=True, nullable=False)
    coins = db.Column(db.Integer, default=0, index=True, nullable=False)

    my_badges = db.relationship('MyBadge', order_by=[MyBadge.created_date.desc()], backref='badge')

    def __repr__(self):
        return 'Badge {}'.format(self.name)

