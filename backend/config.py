# building the API using Flask

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# initialize flask application

app = Flask(__name__)

# wrap app in CORS (disables error -> we can transfer data from different servers)

CORS(app)

# initialize database ------------------------------------------------------------

# specifying the location of the local sqlite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydatabase.db"


# meaning we will not be keeping track of any mods made to the database
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# create an instance of database which allows us access to the DB specified in line 18
db = SQLAlchemy(app)
