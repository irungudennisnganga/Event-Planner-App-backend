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
        
        subject = "Welcome to Event Time!"
        html = "<p>Thank you for signing in!.</p>"
        email_response = send_email(subject, html, user.email)

        return make_response(jsonify({'message': 'Sign up successful', 'email_response': email_response},{'token': access_token}), 200)
        return make_response(jsonify())

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
        
        if not user:
            return make_response(jsonify({'message': 'No user found'}), 400)
        
        subject = "Exited Event Time!"
        html = "<p>Thank you for using our services. User deleted successfuly</p>"
        email_response = send_email(subject, html, user.email)

        # return make_response(jsonify(), 200)
        db.session.delete(user)
        db.session.commit()
        
        return make_response(jsonify({"message":"Deleted successfuly"}), 200)
        
class Events(Resource):
    def get(self):
        expenses = Expense.query.all()
        return jsonify([expense.serialize() for expense in expenses])

    def post(self):
        data = request.json
        if not data:
            return jsonify({'message': 'No input data provided'}), 400

        new_expense = Expense(
            description=data.get('description'),
            amount=data.get('amount'),
            user_id=data.get('user_id'),
            event_id=data.get('event_id'),
            organizer_id=data.get('organizer_id')
        )

        db.session.add(new_expense)
        db.session.commit()

        return jsonify({'message': 'Expense created successfully', 'expense_id': new_expense.id}), 201

# Routes for handling budget-related operations
class Budgets(Resource):
    def get(self):
        budgets = Budget.query.all()
        return jsonify([budget.serialize() for budget in budgets])

    def post(self):
        data = request.json
        if not data:
            return jsonify({'message': 'No input data provided'}), 400

        new_budget = Budget(
            total=data.get('total'),
            event_id=data.get('event_id'),
            organizer_id=data.get('organizer_id')
        )

        db.session.add(new_budget)
        db.session.commit()

        return jsonify({'message': 'Budget created successfully', 'budget_id': new_budget.id}), 201

# Routes for handling event-related operations
class Events(Resource):
    def get(self):
        events = Event.query.all()
        return jsonify([event.serialize() for event in events])

    def post(self):
        data = request.json
        if not data:
            return jsonify({'message': 'No input data provided'}), 400

        new_event = Event(
            title=data['title'],
            date=data['date'],
            time=data['time'],
            location=data['location'],
            description=data['description'],
            category=data['category'],
            organizer_id=data['organizer_id']
        )
        db.session.add(new_event)
        db.session.commit()
        return jsonify({'message': 'Event created successfully', 'event_id': new_event.id}), 201

# Routes for handling resource-related operations
class AllResource(Resource):
    def get(self):
        resources = ResourceModel.query.all()
        return jsonify([resource.serialize() for resource in resources])

    def post(self):
        data = request.json
        if not data:
            return jsonify({'message': 'No input data provided'}), 400

        new_resource = ResourceModel(
            name=data['name'],
            quantity=data['quantity'],
            organizer_id=data['organizer_id'],
            user_id=data['user_id'],
            event_id=data['event_id']
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
