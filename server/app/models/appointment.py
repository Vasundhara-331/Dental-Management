from app import db
from datetime import datetime

class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    tooth_id = db.Column(db.String(10))
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
    estimated_wait_time = db.Column(db.Integer)
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