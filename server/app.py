from config import app, db, api,bcrypt
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from model import User,Event,Rescource as ResourceModel ,Budget, Task, Task_Assignment, Expense
from flask_restful import Resource
from flask import request,jsonify,make_response
from flask_jwt_extended import jwt_manager, create_access_token, get_jwt_identity, jwt_required,unset_jwt_cookies


# from sqlalchemy.exc import IntegrityError
configuration = sib_api_v3_sdk.Configuration()

# Replace "<your brevo api key here>" with your actual SendinBlue API key
configuration.api_key['api-key'] = "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"

# Initialize the SendinBlue API instance
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

def send_email(subject, html, to_address=None, receiver_username=None):
    sender = {"name": "Event Time", "email": "event_time@gmail.com"}
    html_content = html

    # Define the recipient(s)
    if to_address:
        to = [{"email": to_address, "name": receiver_username}]
    else:
        to = [{"email": "eventtime@gmail.com", "name": "Event Time"}]

    # Create a SendSmtpEmail object
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, html_content=html_content, sender=sender, subject=subject)

    try:
        # Send the email
        api_response = api_instance.send_transac_email(send_smtp_email)
        return {"message": "Email sent successfully!"}
    except ApiException as e:
        return {"error": f"Exception when calling SMTPApi->send_transac_email: {e}"}

class UserResource(Resource):  
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')
        user = User.query.filter_by(username=username).first()
        if not username:
            return make_response(jsonify({"message": "Missing username parameter"}), 400)
        if not user or not user.authenticate(password): 
            return {"message": "Invalid username or password"}, 401
        access_token = create_access_token(identity=user.id)
        
        subject = "Welcome to Event Time!"
        html = "<p>Thank you for signing in!.</p>"
        email_response = send_email(subject, html, user.email)

        return make_response(jsonify({'message': 'Sign up successful', 'email_response': email_response}), 200)
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

        # Sending welcome email to the newly signed-up user
        subject = "Welcome to Event Time!"
        html = "<p>Thank you for signing up!. Sign up to continue...</p>"
        email_response = send_email(subject, html, email)

        return make_response(jsonify({'message': 'Sign up successful', 'email_response': email_response}), 200)

#  add Logout method

# add checksession method  
 
class DeleteUser(Resource):
    def delete(self,id):
        # data = request.json
        # username = data.get('username')
        user=User.query.filter_by(id=id).first()
        
        if not user :
            return make_response(jsonify({'message': 'No user found'}), 400)
        
        subject = "Exited Event Time!"
        html = "<p>Thank you for using our services. User deleted successfuly</p>"
        email_response = send_email(subject, html, user.email)

        # return make_response(jsonify(), 200)
        db.session.delete(user)
        db.session.commit()
        
        return make_response(jsonify({"message":"Deleted successfuly"},{'message': 'User deletion successful', 'email_response': email_response}), 200)
    
    
    # add update feature for users to update userdetails
        
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
        
class CheckSession(Resource):
    def get(self):
        if 'user_id' in session:
            user_id = session['user_id']
            return {'message': 'Session is active', 'user_id': user_id}, 200
        else:
            return {'message': 'Session is not active'}, 401
        
class LogoutResource(Resource):
    @jwt_required()  
    def post(self):
        user = get_jwt_identity()

        response = make_response(jsonify({'message': 'Logout successful'}), 200)
        unset_jwt_cookies(response)
        return response


# add Budget Route with GET, POST, DELETE, PATCH

# add Task Routes with GET, POST, DELETE , PATCH

# add Task_management Route with GET, POST, DELETE, PATCH

# add Expense Route withe GET, POST, DELETE, PATCH
            




api.add_resource(LogoutResource, '/logout')
api.add_resource(UserResource, '/login')
api.add_resource(SignupResource, '/sign_up')
api.add_resource(Events, '/events')
api.add_resource(DeleteUser, '/del_user/<int:id>')
api.add_resource(AllResource, '/resource')
api.add_resource(UpdateResource, '/resource/<int:id>')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')




 

if __name__ == '__main__':
    app.run(port=5555, debug=True)   
        