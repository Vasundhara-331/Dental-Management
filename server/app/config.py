import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root:password@localhost/dental_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
    RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')

# server/app/models/user.py
from app import db
from datetime import datetime
import bcrypt

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'doctor', 'patient'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    patient_profile = db.relationship('Patient', backref='user', uselist=False, cascade='all, delete-orphan')
    doctor_profile = db.relationship('Doctor', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.Enum('M', 'F', 'O'))
    address = db.Column(db.Text)
    emergency_contact = db.Column(db.String(15))
    medical_history = db.Column(db.Text)
    allergies = db.Column(db.Text)
    dental_health_score = db.Column(db.Float, default=50.0)
    last_visit = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'address': self.address,
            'emergency_contact': self.emergency_contact,
            'medical_history': self.medical_history,
            'allergies': self.allergies,
            'dental_health_score': self.dental_health_score,
            'last_visit': self.last_visit.isoformat() if self.last_visit else None
        }

class Doctor(db.Model):
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    specialization = db.Column(db.String(100))
    experience_years = db.Column(db.Integer)
    consultation_fee = db.Column(db.Decimal(10, 2))
    available_days = db.Column(db.String(20))  # JSON string of available days
    available_hours = db.Column(db.String(50))  # "09:00-17:00"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'license_number': self.license_number,
            'specialization': self.specialization,
            'experience_years': self.experience_years,
            'consultation_fee': float(self.consultation_fee) if self.consultation_fee else None,
            'available_days': self.available_days,
            'available_hours': self.available_hours
        }

# server/app/models/appointment.py
from app import db
from datetime import datetime

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    tooth_id = db.Column(db.String(10))  # e.g., "UR6"
    symptoms = db.Column(db.Text)
    notes = db.Column(db.Text)
    ai_diagnosis = db.Column(db.Text)
    urgency_score = db.Column(db.Float, default=5.0)
    status = db.Column(db.Enum('scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled'), default='scheduled')
    treatment_notes = db.Column(db.Text)
    prescription = db.Column(db.Text)
    follow_up_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = db.relationship('Patient', backref='appointments')
    doctor = db.relationship('Doctor', backref='appointments')
    queue_entry = db.relationship('QueueEntry', backref='appointment', uselist=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'appointment_date': self.appointment_date.isoformat(),
            'appointment_time': self.appointment_time.strftime('%H:%M'),
            'tooth_id': self.tooth_id,
            'symptoms': self.symptoms,
            'notes': self.notes,
            'ai_diagnosis': self.ai_diagnosis,
            'urgency_score': self.urgency_score,
            'status': self.status,
            'treatment_notes': self.treatment_notes,
            'prescription': self.prescription,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class QueueEntry(db.Model):
    __tablename__ = 'queue_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    queue_position = db.Column(db.Integer, nullable=False)
    estimated_wait_time = db.Column(db.Integer)  # in minutes
    checked_in_at = db.Column(db.DateTime)
    status = db.Column(db.Enum('waiting', 'called', 'in_consultation', 'completed'), default='waiting')
    
    def to_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'queue_position': self.queue_position,
            'estimated_wait_time': self.estimated_wait_time,
            'checked_in_at': self.checked_in_at.isoformat() if self.checked_in_at else None,
            'status': self.status
        }
