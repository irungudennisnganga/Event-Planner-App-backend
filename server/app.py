from config import app, db, api
from model import User
from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_manager, create_access_token
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URL'] = 'sqlites///app.db'
# app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
# db = SQLAlchemy (app)
# jwt  = jwt_manager(app)
class UserResource(Resource):  # Class names should be capitalized
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')
        user = User.query.filter_by(username=username).first()
        if not username:
            return jsonify({"message": "Missing username parameter"}), 400
        if not user or not user.authenticate(password):  # Check if user is None or authentication fails
            return {"message": "Invalid username or password"}, 401
        access_token = create_access_token(identity=user.id)
        return {'token': access_token}

api.add_resource(UserResource, '/login') 

if __name__ == '__main__':
    app.run(port=5555, debug=True)   
        