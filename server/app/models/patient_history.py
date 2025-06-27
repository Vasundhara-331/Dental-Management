from app import db

class PatientHistory(db.Model):
    __tablename__ = 'patient_histories'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    history = db.Column(db.Text)
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'history': self.history
        }
