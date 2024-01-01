from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

db_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db', 'pokemon_tournament.db')
conn_str = 'sqlite:///' + db_file
app.config['SQLALCHEMY_DATABASE_URI'] = conn_str
app.secret_key = os.urandom(12)  # need this so database access will work
db = SQLAlchemy(app)
app.app_context().push()

#  TODO: load starter players(bosses) OK (bosses and my_badges are NOT needed, just pick a random pokemon for fights
#   and compare earned coins with badge value for opacity ONGOING), mypokemon OK, pokemon from result of API call OK,
#   caching pokemon and user (caching user is through current_user OK) (finish videos first OK), db access and relationship OK

# noinspection PyUnresolvedReferences
from program import routes
# noinspection PyUnresolvedReferences
from program.data.__all_models import *

# db.create_all()
# this works because models are imported, but how to check if it has already been created (no need to check?)
# Create tables that do not exist in the database by calling metadata.create_all() for all or some bind keys.
# This does not update existing tables, use a migration library for that.
# This requires that a Flask application context is active.

