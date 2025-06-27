from app import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('pending', 'completed', 'failed', 'refunded'), default='pending')
    method = db.Column(db.Enum('razorpay', 'stripe', 'cash', 'subscription'), nullable=False)
    transaction_id = db.Column(db.String(100))
    subscription_plan = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'appointment_id': self.appointment_id,
            'amount': float(self.amount),
            'status': self.status,
            'method': self.method,
            'transaction_id': self.transaction_id,
            'subscription_plan': self.subscription_plan,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 