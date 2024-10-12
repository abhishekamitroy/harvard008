from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)


# Configure SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prepcheck.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', '76d07ad979f9436ca43b3534b806b6e1761fda04e3c94c0f52122274341213d4')
jwt = JWTManager(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Patient Model
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

# Staff Model
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

# User Registration
@app.route('/register', methods=['POST'])
def register():
    logger.info("Register endpoint reached")
    try:
        data = request.get_json()
        logger.debug(f"Received registration data: {data}")
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({"error": "Missing username or password"}), 400
        
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            return jsonify({"error": "Username already exists"}), 400

        hashed_password = generate_password_hash(data['password'])  # Remove the method parameter
        new_user = User(username=data['username'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"User registered successfully: {data['username']}")
        return jsonify({"message": "User registered successfully!"}), 201
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/login', methods=['POST'])
def login():
    logger.info("Login endpoint reached")
    try:
        data = request.get_json()
        logger.debug(f"Received login data: {data}")
        
        if not data or 'username' not in data or 'password' not in data:
            logger.warning("Request data missing username or password")
            return jsonify({"error": "Missing username or password"}), 400

        user = User.query.filter_by(username=data['username']).first()
        if not user:
            logger.warning(f"User not found: {data['username']}")
            return jsonify({"error": "Invalid credentials"}), 401

        if not check_password_hash(user.password, data['password']):
            logger.warning(f"Password check failed for user: {data['username']}")
            return jsonify({"error": "Invalid credentials"}), 401

        access_token = create_access_token(identity=user.username)
        logger.info(f"Login successful for user: {data['username']}")
        return jsonify(access_token=access_token), 200
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# User Logout
@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({"message": "Logged out!"}), 200

# Routes for Patients
@app.route('/patients', methods=['POST'])
@jwt_required()
def add_patient():
    try:
        data = request.get_json()
        current_user = get_jwt_identity()
        surgery_date = datetime.strptime(data['surgery_date'], '%Y-%m-%d').date()

        new_patient = Patient(
            name=data['name'],
            medical_history=data.get('medical_history', ''),
            surgery_date=surgery_date
        )

        db.session.add(new_patient)
        db.session.commit()

        return jsonify({"message": f"Patient added by {current_user}"}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/patients', methods=['GET'])
@jwt_required()
def get_patients():
    patients = Patient.query.all()
    return jsonify([patient.to_dict() for patient in patients]), 200

# Routes for Staff
@app.route('/staff', methods=['POST'])
@jwt_required()
def add_staff():
    try:
        data = request.get_json()
        new_staff = Staff(
            name=data['name'],
            role=data['role'],
            credentials=data['credentials']
        )
        db.session.add(new_staff)
        db.session.commit()
        return jsonify(new_staff.to_dict()), 201
    except Exception as e:
        print(f"Error adding staff: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/staff', methods=['GET'])
@jwt_required()
def get_staff():
    staff_members = Staff.query.all()
    return jsonify([staff.to_dict() for staff in staff_members]), 200

@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "username": user.username} for user in users]), 200

@app.before_request
def log_request_info():
    logger.debug('Headers: %s', request.headers)
    logger.debug('Body: %s', request.get_data())

@app.after_request
def log_response_info(response):
    logger.debug('Response Status: %s', response.status)
    logger.debug('Response: %s', response.get_data())
    return response

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
