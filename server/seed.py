from datetime import datetime, time
from model import User, Event, Task, Budget, Rescource, Expense, Task_Assignment
from config import db,app

with app.app_context():  # Create an application context
    users = User.query.all()
    for user in users:
        db.session.delete(user)
    db.session.commit()

    user1 = User(username='John', email='john@example.com', first_name='Mary', last_name='Doe')
    user2 = User(username='Jane', email='jane@example.com', first_name='James', last_name='Smith')

    db.session.add_all([user1, user2])
    db.session.commit()

    event1 = Event(title='Birthday Party', date=datetime(2022, 5, 15), time=time(14, 0), location='Home', description='Party for my son', category='Birthday', organizer_id=user1.id)
    event2 = Event(title='Corporate Event', date=datetime(2022, 6, 20), time=time(10, 0), location='Office', description='Annual company event', category='Corporate', organizer_id=user2.id)

    db.session.add_all([event1, event2])
    db.session.commit()

    resource1 = Rescource(name='Table', quantity=1, user_id=user1.id, event_id=event1.id)
    resource2 = Rescource(name='Chairs', quantity=10, user_id=user1.id, event_id=event1.id)
    resource3 = Rescource(name='Laptop', quantity=1, user_id=user2.id, event_id=event2.id)

    db.session.add_all([resource1, resource2, resource3])
    db.session.commit()

    task1 = Task(title='Buy a birthday cake', deadline=time(13, 0), completed=False, user_id=user1.id, event_id=event1.id)
    task2 = Task(title='Prepare presentation', deadline=time(9, 0), completed=False, user_id=user2.id, event_id=event2.id)

    db.session.add_all([task1, task2])
    db.session.commit()

    budget1 = Budget(total=500, event_id=event1.id)
    budget2 = Budget(total=2000, event_id=event2.id)

    db.session.add_all([budget1, budget2])
    db.session.commit()

    expense1 = Expense(description='Birthday Cake', amount=100, user_id=user1.id, event_id=event1.id)
    expense2 = Expense(description='Catering', amount=500, user_id=user2.id, event_id=event2.id)

    db.session.add_all([expense1, expense2])
    db.session.commit()

    task_assignment1 = Task_Assignment(task_id=task1.id, user_id=user1.id, deadline=time(13, 0), completed=False)
    task_assignment2 = Task_Assignment(task_id=task2.id, user_id=user2.id, deadline=time(9, 0), completed=False)

    db.session.add_all([task_assignment1, task_assignment2])
    db.session.commit()