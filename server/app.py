from config import app, db, api,bcrypt
from model import User,Event,Rescource as ResourceModel 
from flask_restful import Resource
from flask import request, session,jsonify,make_response
from flask_jwt_extended import jwt_manager, create_access_token
from sqlalchemy.exc import IntegrityError

class UserResource(Resource):  # Class names should be capitalized
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')
        user = User.query.filter_by(username=username).first()
        if not username:
            return make_response(jsonify({"message": "Missing username parameter"}), 400)
        if not user or not user.authenticate(password):  # Check if user is None or authentication fails
            return {"message": "Invalid username or password"}, 401
        access_token = create_access_token(identity=user.id)
        return make_response(jsonify({'token': access_token}))

class SignupResource(Resource):
    def post(self):
        data = request.json
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([first_name, last_name, username, email, password]):
            return make_response(jsonify({'errors': ['Missing required data']}), 400)

        if User.query.filter_by(username=username).first():
            return make_response(jsonify({'message': 'User already exists'}), 400)

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            _password_hash=bcrypt.generate_password_hash(password).decode('utf-8')
        )
        db.session.add(new_user)
        db.session.commit()

        return make_response(jsonify({'message': 'Sign up successful'}), 200)
    
    # change username to be enterd through routes
class DeleteUser(Resource):
    def delete(self):
        data = request.json
        username = data.get('username')
        user=User.query.filter_by(username=username).first()
        
        if not user :
            return make_response(jsonify({'message': 'No user found'}), 400)
        
        db.session.delete(user)
        db.session.commit()
        
        return make_response(jsonify({"message":"Deleted successfuly"}), 200)
        
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
   
class AllResource(Resource):
    def get(self):
        resources = [resource.serialize() for resource in ResourceModel.query.all()]  
        return make_response(jsonify(resources))
    
    def post(self):
        name = request.get_json()['name'] 
        quantity = request.get_json()['quantity'] 
        organizer_id = request.get_json()['organizer_id'] 
        user_id = request.get_json()['user_id'] 
        event_id = request.get_json()['event_id'] 
        
        if name is None or quantity is None or user_id is None or event_id is None or organizer_id is None :
            return make_response(jsonify({'errors': ['Missing required data']}), 400)
        
        new_resource =ResourceModel(
            name=name,
            quantity=quantity,
            organizer_id=organizer_id,
            user_id=user_id,
            event_id=event_id
        )
        db.session.add(new_resource)
        db.session.commit()
        
class UpdateResource(Resource):
        def patch(self,id):
            data = request.get_json()
            resource = ResourceModel.query.filter_by(id=id).first()
            if not resource:
                return make_response(jsonify({'message': 'Resource not found'}), 404)


            if 'name' in data:
                resource.name = data['name']
            if 'quantity' in data:
                resource.quantity = data['quantity']
            if 'organizer_id' in data:
                resource.organizer_id = data['organizer_id']
            if 'user_id' in data:
                resource.user_id = data['user_id']
            if 'event_id' in data:
                resource.event_id = data['event_id']

            db.session.commit()
            
            return make_response(jsonify({'message': 'Resource updated successfully'}), 200)   
        
        def delete(self,id):
            resource = ResourceModel.query.filter_by(id=id).first()

            db.session.delete(resource)
            db.session.commit()
            
            return make_response(jsonify({'message': 'Resource deleted successfully'}), 200)


            
         
api.add_resource(Events, '/events')
api.add_resource(UserResource, '/login')
api.add_resource(SignupResource, '/add_user')
api.add_resource(DeleteUser, '/del_user')
api.add_resource(AllResource, '/resource')
api.add_resource(UpdateResource, '/resource/<int:id>')


 

if __name__ == '__main__':
    app.run(port=5555, debug=True)   
        