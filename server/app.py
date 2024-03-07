from config import app, db, api,bcrypt
from model import User,Event
from flask_restful import Resource
from flask import request, session,jsonify,make_response
from flask_jwt_extended import jwt_manager, create_access_token


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

   
class AddUser(Resource):
    def post(self):
        first_name =request.json.get('first_name')
        last_name =request.json.get('last_name')
        username =request.json.get('username')
        email =request.json.get('email')
        password =request.json.get('password')

        if first_name is None or last_name is None or username is None or email is None or password is None:
            return make_response(jsonify({'errors': ['Missing required data']}), 400)
        
        new_user =User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            _password_hash=bcrypt.generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()


class Events(Resource):
    def get(self):
        events = [event.serialize() for event in Event.query.all()]
        
        response = make_response(
            jsonify(events),
            200
        )
        
        return response
    
    def post(self):
        title = request.get_json()['title'] 
        date = request.get_json()['date'] 
        time = request.get_json()['time'] 
        location = request.get_json()['location'] 
        description = request.get_json()['description'] 
        category = request.get_json()['category'] 
        organizer_id = request.get_json()['organizer_id'] 
        
        if time is None or title is None or date is None or location is None or description is None or category is None or organizer_id is None:
            return make_response(jsonify({'errors': ['Missing required data']}), 400)
        
        new_event = Event(
            title=title,
            date=date,
            time=time,
            location=location,
            description=description,
            category=category,
            organizer_id=organizer_id
        )
        
        db.session.add(new_event)
        db.session.commit()
        
api.add_resource(Events, '/events')
api.add_resource(UserResource, '/login')
api.add_resource(AddUser, '/add_user')


 

if __name__ == '__main__':
    app.run(port=5555, debug=True)   
        