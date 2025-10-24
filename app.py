from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import create_engine
import os

app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'events.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Separate database for registrations to keep registration data isolated
app.config['SQLALCHEMY_BINDS'] = {
    'registrations': 'sqlite:///' + os.path.join(basedir, 'registrations.db')
}

db = SQLAlchemy(app)

# Registration Model
class Registration(db.Model):
    # store registrations in a separate DB file (bind 'registrations')
    __bind_key__ = 'registrations'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, nullable=False)
    # keep a snapshot of the event name to avoid cross-db foreign keys
    event_name = db.Column(db.String(200), nullable=False)
    # the council (e.g., GDSC, CSI) captured at registration time
    council = db.Column(db.String(100), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    class_name = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    roll_no = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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

    def is_registration_open(self):
        today = datetime.now().strftime('%Y-%m-%d')
        return today <= self.end_date

@app.route('/')
def home():
    return render_template('home.html')

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
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('events.html', events=events, total_events=len(events), today=today)


@app.route('/registrations')
def view_registrations():
    # show all registrations with related event name (public view restored)
    regs = Registration.query.order_by(Registration.created_at.desc()).all()
    return render_template('registrations.html', registrations=regs)

@app.route('/event/<int:event_id>/register', methods=['POST'])
def register_event(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        app.logger.info('Register attempt for event_id=%s from form keys=%s', event_id, list(request.form.keys()))

        if not event.is_registration_open():
            return jsonify({"success": False, "message": "Registration is closed"}), 400

        data = request.form
        # basic validation
        name = data.get('name', '').strip()
        class_name = data.get('class_name', '').strip()
        year = data.get('year', '').strip()
        roll_no = data.get('roll_no', '').strip()
        if not (name and class_name and year and roll_no):
            return jsonify({"success": False, "message": "All fields are required"}), 400

        try:
            year_int = int(year)
        except ValueError:
            return jsonify({"success": False, "message": "Year must be a number"}), 400

        registration = Registration(
            event_id=event_id,
            event_name=event.name,
            council=event.council,
            name=name,
            class_name=class_name,
            year=year_int,
            roll_no=roll_no
        )

        db.session.add(registration)
        db.session.commit()

        return jsonify({"success": True, "message": "Registration successful"})
    except Exception as e:
        # ensure we always return JSON (avoid HTML debug page reaching client)
        app.logger.exception('Error in register_event')
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/event/<int:event_id>/unregister', methods=['POST'])
def unregister_event(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        data = request.form
        roll_no = data.get('roll_no')
        if not roll_no:
            return jsonify({"success": False, "message": "roll_no required"}), 400

        reg = Registration.query.filter_by(event_id=event_id, roll_no=roll_no).first()
        if not reg:
            return jsonify({"success": False, "message": "Registration not found"}), 404

        db.session.delete(reg)
        db.session.commit()
        return jsonify({"success": True, "message": "Unregistered successfully"})
    except Exception as e:
        app.logger.exception('Error in unregister_event')
        return jsonify({"success": False, "message": str(e)}), 500

def init_db():
    with app.app_context():
        # Create tables for default bind and named binds
        db.create_all()
        # ensure binds' tables are created
        for bind, uri in app.config.get('SQLALCHEMY_BINDS', {}).items():
            # create tables for each configured bind using a dedicated engine
            engine = create_engine(uri)
            db.metadata.create_all(bind=engine)
        # Clear existing events and reset the sequence
        Event.query.delete()
        db.session.commit()
        
        # Add sample data
        sample_events = [
            Event(
                name="BitnBuild",
                council="GDSC",
                start_date="2025-11-15",
                end_date="2025-11-16",
                venue="College Auditorium"
            ),
            Event(
                name="Internship Expo",
                council="TedxCrce",
                start_date="2025-12-01",
                end_date="2025-12-03",
                venue="College Ground"
            ),
            Event(
                name="Euphoria'25 ",
                council="StudentsCouncil",
                start_date="2025-10-25",
                end_date="2025-10-25",
                venue="Computer Labs"
            ),
            Event(
                name="Trek",
                council="Rotaract",
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