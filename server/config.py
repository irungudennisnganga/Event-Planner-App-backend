from flask import Flask # import flask
from flask_migrate import Migrate # import migration
from flask_restful import Api # import cors
import os
from flask_sqlalchemy import SQLAlchemy # import sqlalchemy
from flask_cors import CORS # import cors
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from app import CheckSession  # Import the CheckSession class from resources module


app = Flask(__name__) #instanciate a flask application 

app.secret_key = b'\xc2A\x1c\xc6\xc5QvJ?ZH$\x13\\4\xb0'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'ce81d8454bd966ba09bbbdf723f632fd'
app.add_resource(CheckSession, '/check_session', endpoint='check_session')

# app.json.compact = False
jwt  = JWTManager(app)

CORS(app)

db = SQLAlchemy()
migrate = Migrate(app, db)
db.init_app(app)
bcrypt=Bcrypt(app)



api = Api(app)
