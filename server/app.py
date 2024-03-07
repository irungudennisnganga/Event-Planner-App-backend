from config import app, db, api
from model import User,Event
from flask_restful import Resource
from flask import request, session,jsonify,make_response

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


if __name__ == '__main__':
    app.run(port=5555, debug=True)   
        