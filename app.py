from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'events.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Event Model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    council = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.String(10), nullable=False)
    end_date = db.Column(db.String(10), nullable=False)
    venue = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'council': self.council,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'venue': self.venue
        }

@app.route('/')
def home():
    return 'Welcome to CrceConnect!'

@app.route('/about')
def about():
    return 'About CrceConnect'

@app.route('/api/events', methods=['GET'])
def get_events():
    events = Event.query.order_by(Event.start_date).all()
    return jsonify({
        "success": True,
        "events": [event.to_dict() for event in events],
        "total_events": len(events)
    })

@app.route('/api/events', methods=['POST'])
def create_event():
    data = request.json
    new_event = Event(
        name=data['name'],
        council=data['council'],
        start_date=data['start_date'],
        end_date=data['end_date'],
        venue=data['venue']
    )
    db.session.add(new_event)
    db.session.commit()
    return jsonify({"success": True, "event": new_event.to_dict()}), 201

@app.route('/events')
def display_events():
    events = Event.query.order_by(Event.start_date).all()
    return render_template('events.html', events=events, total_events=len(events))

def init_db():
    with app.app_context():
        db.create_all()
        # Add sample data if database is empty
        if not Event.query.first():
            sample_events = [
                Event(
                    name="Tech Symposium 2025",
                    council="IEEE Student Council",
                    start_date="2025-11-15",
                    end_date="2025-11-16",
                    venue="College Auditorium"
                ),
                Event(
                    name="Cultural Fest",
                    council="Cultural Council",
                    start_date="2025-12-01",
                    end_date="2025-12-03",
                    venue="College Ground"
                ),
                Event(
                    name="Code Sprint",
                    council="CSI Student Chapter",
                    start_date="2025-10-25",
                    end_date="2025-10-25",
                    venue="Computer Labs"
                )
            ]
            for event in sample_events:
                db.session.add(event)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)