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

# noinspection PyUnresolvedReferences
from program import routes
# noinspection PyUnresolvedReferences
from program.data.__all_models import *


