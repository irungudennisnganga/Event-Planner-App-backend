from config import app, db, api,bcrypt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from model import User,Event,Rescource as ResourceModel ,Budget, Task, Task_Assignment, Expense
from flask_restful import Resource
from flask import request,jsonify,make_response,session
from flask_jwt_extended import jwt_manager, create_access_token, get_jwt_identity, jwt_required,unset_jwt_cookies
from datetime import datetime,timedelta

def send_email(email,subject,body):
    
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'dennis.irungu@student.moringaschool.com'
    sender_password = 'eenk dqxl hwwv kmxv'
    subject=subject
    body=body

    message = f'Subject: {subject}\n\n{body}'

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email,email,message)
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
        html = "Thank you for signing in!"
        email_response= send_email(user.email,subject,html)

        return make_response(jsonify({'message': 'Sign in successful', 'email_response': email_response},{'token': access_token}), 200)
        # return make_response(jsonify())

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
        subject =  "Welcome to Event Time!"
        body = f'Thank you for signing up!. Sign up to continue...'
        
        send_email(email,subject,body)
        
        access_token = create_access_token(identity=new_user.id)

        return make_response(jsonify({'message': 'Sign up successful'},{'token': access_token}), 200)

#  add Logout method
class CheckSession(Resource):
    @jwt_required() 
    def get(self):
        user_id = get_jwt_identity()
        
        user= User.query.filter_by(id=user_id).first()
        
        if  not user :
            return {"message":"user not found"}
        
        user_data = {
            "user_id":user.id,
            "username":user.username
        }    
        
        return make_response(jsonify(user_data), 200)
            
     
 
class DeleteUser(Resource):
    @jwt_required()
    def delete(self):
        # data = request.json
        # username = data.get('username')
        user_id = get_jwt_identity()
        user=User.query.filter_by(id=user_id).first()
        
        if not user :
            return make_response(jsonify({'message': 'No user found'}), 400)
        
        subject = "Exited Event Time!"
        html = "Thank you for using our services. User deleted successfuly"
        email_response = send_email( user.email,subject, html)

        # return make_response(jsonify(), 200)
        db.session.delete(user)
        db.session.commit()
        
        return make_response(jsonify({"message":"Deleted successfuly"},{'message': 'User deletion successful'}), 200)
    
    
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
        data = request.get_json()
        
        title = data.get('title')
        date_str = data.get('date')
        time_str = data.get('time')
        location = data.get('location')
        description = data.get('description')
        category = data.get('category')
        organizer_id = data.get('organizer_id')
        
        if not all([title, date_str, time_str, location, description, category, organizer_id]):
            return make_response(jsonify({'errors': ['Missing required data']}), 400)
        
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            time = datetime.strptime(time_str, '%H:%M:%S').time()
        except ValueError:
            return make_response(jsonify({'errors': ['Invalid date or time format']}), 400)
        
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
class EventHandler(Resource):
    def patch(self, id):
        data = request.get_json()
        event = Event.query.filter_by(id=id).first()
        if not event:
            return make_response(jsonify({'message': 'Event not found'}), 404)
        
        try:
            if 'category' in data:
                event.category = data['category']
            if 'date' in data:
                # Ensure the date is in the correct format
                event.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            if 'organizer_id' in data:
                event.organizer_id = data['organizer_id']
            if 'description' in data:
                event.description = data['description']
            if 'location' in data:
                event.location = data['location']
            if 'time' in data:
                # Convert time string to Python time object
                event.time = datetime.strptime(data['time'], '%H:%M:%S').time()
            if 'title' in data:
                event.title = data['title']
            
            db.session.commit()
            return make_response(jsonify({'message': 'Event updated successfully'}), 200)
        except ValueError:
            return make_response(jsonify({'error': 'Invalid date or time format'}), 400)
        
    def delete(self, id):
        event = Event.query.filter_by(id=id).first()
        
        if not event:
            return make_response(jsonify({'message': 'No Event'}), 404)

        # Ensure to delete associated resources before deleting the event
        for resource in event.resources:
            db.session.delete(resource)

        db.session.delete(event)
        db.session.commit()
        
        return make_response(jsonify({'message': 'Event deleted successfully'}), 200)
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
            
            if not resource:
                return make_response(jsonify({'message': 'No resource'}), 200)

            db.session.delete(resource)
            db.session.commit()
            
            return make_response(jsonify({'message': 'Resource deleted successfully'}), 200)
        


# add Budget Route with GET, POST, DELETE, PATCH

# add Expense Route withe GET, POST, DELETE, PATCH

# add Task 
        # Add Budget Route with GET, POST, DELETE, PATCH
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

    def delete(self):
        # Implement delete functionality here
        pass

    def patch(self):
        # Implement patch functionality here
        pass

# Add Expense Route with GET, POST, DELETE, PATCH
class Expenses(Resource):
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

    def delete(self):
        # Implement delete functionality here
        pass

    def patch(self):
        # Implement patch functionality here
        pass

# Add these routes to your API
api.add_resource(Expenses, '/expenses')
api.add_resource(Budgets, '/budgets')

class AllTask(Resource):
    def get(self):
        task = [resource.serialize() for resource in Task.query.all()]
        
        return make_response(jsonify(task))
    
    def post(self):
        title = request.get_json()['title'] 
        deadline = request.get_json()['deadline'] 
        completed = request.get_json()['completed'] 
        organizer_id = request.get_json()['organizer_id']
        user_id =request.get_json()['user_id'] 
        event_id = request.get_json()['event_id'] 
        
        deadline_datetime = datetime.strptime(deadline, "%Y-%m-%d")
        
        if title is None or deadline is None or completed is None or organizer_id is None or user_id is None or event_id is None:
            return make_response(jsonify({'errors': ['Missing required data']}), 400)
        
        new_task = Task(
            title=title,
            deadline=deadline_datetime,
            completed=completed,
            organizer_id=organizer_id,
            user_id=user_id,
            event_id=event_id
        )
        
        db.session.add(new_task)
        db.session.commit()
        
        return make_response(jsonify({'message': 'added successfuly'}), 200)

class UpdateDeleteTask(Resource):
        def patch(self,id):
            data = request.get_json()
            task = Task.query.filter_by(id=id).first()
            if not task:
                return make_response(jsonify({'message': 'Task not found'}), 404)


            if 'title' in data:
                task.title = data['title']
            if 'deadline' in data:
                task.deadline = data['deadline']
            if 'organizer_id' in data:
                task.organizer_id = data['organizer_id']
            if 'completed' in data:
                task.completed = data['completed']
            if 'event_id' in data:
                task.event_id = data['event_id']
                
            if 'user_id' in data:
                task.user_id =data['user_id']

            db.session.commit()
            
            return make_response(jsonify({'message': 'Task updated successfully'}), 200)   
        
        def delete(self,id):
            task = Task.query.filter_by(id=id).first()
            if not task:
                return make_response(jsonify({'message': 'No task'}), 200) 
                

            db.session.delete(task)
            db.session.commit()
            
            return make_response(jsonify({'message': 'Task deleted successfully'}), 200)             
        
# add Task_management Route with GET, POST, DELETE, PATCH
class AllTask_management(Resource):
    def get(self):
        task = [resource.serialize() for resource in Task_Assignment.query.all()]
        
        return make_response(jsonify(task))
    
    def post(self):
        task_id = request.get_json()['task_id'] 
        user_id = request.get_json()['user_id'] 
        organizer_id = request.get_json()['organizer_id'] 
        completed = request.get_json()['completed']
        
        
        if task_id is None or user_id is None or organizer_id is None:
            return make_response(jsonify({'errors': ['Missing required data']}), 400)
        
        new_task_management=Task_Assignment(
            task_id=task_id,
            user_id=user_id,
            organizer_id=organizer_id,
            completed=completed
        )
        
        db.session.add(new_task_management)
        db.session.commit()
        
        return make_response(jsonify({'message': 'Task assignment added successfully'}), 200)
 
class UpdateTaskAssignment(Resource):
        def patch(self,id):
            data = request.get_json()
            task_assignment = Task_Assignment.query.filter_by(id=id).first()
            if not task_assignment:
                return make_response(jsonify({'message': 'Task_assignment not found'}), 404)


            if 'task_id' in data:
                task_assignment.task_id = data['task_id']
            if 'organizer_id' in data:
                task_assignment.organizer_id = data['organizer_id']
            if 'completed' in data:
                task_assignment.completed = data['completed']
            if 'user_id' in data:
                task_assignment.user_id =data['user_id']

            db.session.commit()
            
            return make_response(jsonify({'message': 'Task_assignment updated successfully'}), 200)   
        
        def delete(self,id):
            task_assignment = Task_Assignment.query.filter_by(id=id).first()
            if not task_assignment:
                return make_response(jsonify({'message': 'No task_assignment'}), 200) 
                

            db.session.delete(task_assignment)
            db.session.commit()
            
            return make_response(jsonify({'message': 'Task_assignment deleted successfully'}), 200)             

def send_email_notification(recipient, subject, body):
    # Set up the SMTP server
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_server.starttls()
    smtp_server.login('dennis.irungu@student.moringaschool.com', 'eenk dqxl hwwv kmxv')

    # Create message
    msg = MIMEMultipart()
    msg['From'] = 'dennis.irungu@student.moringaschool.com'
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send email
    smtp_server.send_message(msg)
    smtp_server.quit()

def send_task_deadline_notifications():
    # Get tasks with approaching deadlines
    approaching_deadline_tasks = Task.query.filter(Task.deadline <= datetime.now(), 
                                       Task.deadline <= datetime.now() + timedelta(days=7)).all()
    print(approaching_deadline_tasks)
    for task in approaching_deadline_tasks:
        # Get users assigned to the task
        assigned_users = [assignment.user.email for assignment in task.task_assignment]
        # Prepare email content
        subject = f'Upcoming Deadline: {task.title}'
        body = f'Dear User,\n\nThis is a reminder that the deadline for the task "{task.title}" is approaching. Please make sure to complete it on time that is {task.deadline}.\n\nBest regards,\nThe Event Planner Team'
        # Send email notifications to assigned users
        for user_email in assigned_users:
            send_email_notification(user_email, subject, body)
            
            
            
# api.add_resource(LogoutResource, '/logout')
api.add_resource(UserResource, '/login')
api.add_resource(SignupResource, '/sign_up')
api.add_resource(Events, '/events')
api.add_resource(EventHandler ,'/events/<int:id>')
api.add_resource(DeleteUser, '/del_user')
api.add_resource(AllResource, '/resource')
api.add_resource(UpdateResource, '/resource/<int:id>',endpoint='resource')
api.add_resource(UpdateDeleteTask, '/task_update/<int:id>')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(AllTask, '/task' )
api.add_resource(AllTask_management, '/task_management')
api.add_resource(UpdateTaskAssignment, '/task_management/<int:id>')


with app.app_context():
    send_task_deadline_notifications() 

if __name__ == '__main__':
    app.run(port=5555, debug=True) 
     
        