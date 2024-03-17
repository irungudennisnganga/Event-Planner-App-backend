from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property
from config import db
from sqlalchemy import UniqueConstraint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from config import db,bcrypt
from datetime import datetime
# db = SQLAlchemy()


from sqlalchemy import UniqueConstraint

class Resource(db.Model, SerializerMixin):
    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    organizer_id = db.Column(db.Integer)
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)

    __table_args__ = (UniqueConstraint('name', name='unique_name'),)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    
    def serialize(self):
        return {
            'id': self.id,
            'name':self.name,
            'quantity':self.quantity,
            
            'organizer_id': self.organizer_id,
            'event_id': self.event_id,
        }

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False, unique=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    
    event = db.relationship("Event", backref='user')
    task_assignment = db.relationship("Task_Assignment", backref='user')
    # task = db.relationship('Task', backref='user')
    expenses = db.relationship('Expense', backref='user')
    # rescources = db.relationship('Resource', backref='user') 
    
    def serialize(self):
        return {
            'id': self.id,
            'first_name':self.first_name,
            'last_name':self.last_name,
            'username':self.username,
            'email': self.email
            
    }
    @validates('email')
    def validate_email(self, key, value):
        if '@' not in value and '.com' not in value:
            raise ValueError("Invalid email")
        return value
    
    @hybrid_property
    def password_hash(self):
        return self._password_hash

    @password_hash.setter
    def password_hash(self,password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self,password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8'))
    
    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"

       
    
class Event(db.Model, SerializerMixin):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    location = db.Column(db.String)
    description = db.Column(db.String)
    category = db.Column(db.String)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    # tasks = db.relationship("Task", backref='event')
    resources = db.relationship('Resource', backref='event')  # Fixed typo in resource
    expenses = db.relationship('Expense', backref='event')

    budget = db.relationship('Budget', backref='event', lazy="select", uselist=False)  

    def serialize(self):
        serialized_date = self.date.strftime('%Y-%m-%d') if self.date else None
        serialized_time = self.time.strftime('%H:%M') if self.time else None
        
        return {
            'id': self.id,
            'title': self.title,
            'date': serialized_date,
            'time': serialized_time,
            'location': self.location,
            'description': self.description,
            'category': self.category,
            'organizer_id': self.organizer_id,
            # 'tasks': [task.serialize() for task in self.tasks] if self.tasks else []  # Serialize tasks if needed
        }



class Task(db.Model, SerializerMixin):
    __tablename__ = 'tasks' 

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    deadline = db.Column(db.String)
    completed = db.Column(db.String)
    organizer_id = db.Column(db.Integer)
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    
    task_assignment = db.relationship('Task_Assignment', backref='task')
    
    def serialize(self):
        deadline_datetime = None
        if self.deadline:
            try:
                deadline_str = str(self.deadline)
                deadline_datetime = datetime.strptime(deadline_str, '%Y-%m-%d')
            except ValueError:
                # Handle invalid date format gracefully
                deadline_datetime = None

        return {
            'id': self.id,
            'title': self.title,
            'deadline': deadline_datetime.strftime('%Y-%m-%d') if deadline_datetime else None,
            'completed': self.completed,
            'event_id': self.event_id,
            'organizer_id': self.organizer_id
        }


class Task_Assignment(db.Model, SerializerMixin):
    __tablename__ ='task_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    user_id = db.Column(db.Integer , db.ForeignKey('users.id'))
    organizer_id = db.Column(db.Integer)

    completed = db.Column(db.Boolean, default=False)
    
    def serialize(self):
        return {
            'id': self.id,
            'task_id':self.task_id,
            'user_id':self.user_id,
            'organizer_id': self.organizer_id,
            'completed':self.completed
            
    }
    

class Budget(db.Model,SerializerMixin):
    __tablename__ ='budgets'   
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    organizer_id = db.Column(db.Integer)
    total = db.Column(db.Integer)
    
    def serialize(self):
        return {
            'id': self.id,
            'organizer_id': self.organizer_id,
            'event_id': self.event_id,
            'total':self.total
            
    }
    

class Expense(db.Model, SerializerMixin):
    __tablename__ ='expenses'

    id = db.Column(db.Integer, primary_key=True)
    description =db.Column(db.String)
    amount = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id =db.Column(db.Integer, db.ForeignKey('events.id'))
    organizer_id = db.Column(db.Integer)

    created_at =db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    
    def serialize(self):
        return {
            'id': self.id,
            'description':self.description,
            'amount':self.amount,
            'user_id':self.user_id,
            'organizer_id': self.organizer_id,
            'event_id': self.event_id,
            
    }

    
    



