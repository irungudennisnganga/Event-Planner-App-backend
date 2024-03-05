from flask import Flask # import flask
from flask_migrate import Migrate # import migration
from flask_restful import Api # import cors
import os
from flask_sqlalchemy import SQLAlchemy # import sqlalchemy
from flask_cors import CORS # import cors

app = Flask(__name__) #instanciate a flask application 

app.secret_key = b'\xc2A\x1c\xc6\xc5QvJ?ZH$\x13\\4\xb0'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
# db.init_app(app)



api = Api(app)
