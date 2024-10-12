#imports
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)

#Configure SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prepcheck.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    medical_history = db.Column(db.Text, nullable=True)
    surgery_date = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "medical_history": self.medical_history,
            "surgery_date": self.surgery_date.isoformat()
        }

class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    credentials = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "credentials": self.credentials
        }

# Routes for Patients
@app.route('/patients', methods=['POST'])
def add_patient():
    try:
        data = request.get_json()

        # Convert the surgery_date string to a date object
        surgery_date = datetime.strptime(data['surgery_date'], '%Y-%m-%d').date()

        new_patient = Patient(
            name=data['name'],
            medical_history=data.get('medical_history', ''),
            surgery_date=surgery_date
        )

        db.session.add(new_patient)
        db.session.commit()

        return jsonify(new_patient.to_dict()), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/patients', methods=['GET'])
def get_patients():
    patients = Patient.query.all()
    return jsonify([patient.to_dict() for patient in patients]), 200

# Routes for Staff
@app.route('/staff', methods=['POST'])
def add_staff():
    data = request.get_json()
    new_staff = Staff(
        name=data['name'],
        role=data['role'],
        credentials=data['credentials']
    )
    db.session.add(new_staff)
    db.session.commit()
    return jsonify(new_staff.to_dict()), 201

@app.route('/staff', methods=['GET'])
def get_staff():
    staff_members = Staff.query.all()
    return jsonify([staff.to_dict() for staff in staff_members]), 200

if __name__ == '__main__':
    app.run(debug=True)