from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, socketio
from app.models.appointment import Appointment, QueueEntry
from app.models.user import User
from datetime import datetime, date

queue_bp = Blueprint('queue', __name__)

@queue_bp.route('/status/<int:appointment_id>', methods=['GET'])
@jwt_required()
def get_queue_status(appointment_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
        
        # Check authorization
        if user.role == 'patient' and appointment.patient.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        queue_entry = QueueEntry.query.filter_by(appointment_id=appointment_id).first()
        
        if not queue_entry:
            return jsonify({'error': 'Queue entry not found'}), 404
        
        # Count patients ahead in queue
        patients_ahead = QueueEntry.query.filter(
            QueueEntry.queue_position < queue_entry.queue_position,
            QueueEntry.status.in_(['waiting', 'called'])
        ).count()
        
        return jsonify({
            'queue_position': queue_entry.queue_position,
            'patients_ahead': patients_ahead,
            'estimated_wait_time': queue_entry.estimated_wait_time,
            'status': queue_entry.status,
            'checked_in_at': queue_entry.checked_in_at.isoformat() if queue_entry.checked_in_at else None
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@queue_bp.route('/checkin/<int:appointment_id>', methods=['POST'])
@jwt_required()
def checkin_patient(appointment_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
        
        # Check authorization
        if user.role == 'patient' and appointment.patient.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Check if appointment is for today
        if appointment.appointment_date != date.today():
            return jsonify({'error': 'Can only check in for today\'s appointments'}), 400
        
        # Create or update queue entry
        queue_entry = QueueEntry.query.filter_by(appointment_id=appointment_id).first()
        
        if not queue_entry:
            # Get next queue position
            max_position = db.session.query(db.func.max(QueueEntry.queue_position)).scalar() or 0
            
            queue_entry = QueueEntry(
                appointment_id=appointment_id,
                queue_position=max_position + 1,
                estimated_wait_time=30,  # Default 30 minutes
                checked_in_at=datetime.utcnow()
            )
            db.session.add(queue_entry)
        else:
            queue_entry.checked_in_at = datetime.utcnow()
            queue_entry.status = 'waiting'
        
        db.session.commit()
        
        # Emit real-time update
        socketio.emit('patient_checked_in', {
            'appointment_id': appointment_id,
            'queue_position': queue_entry.queue_position,
            'patient_name': f"{user.first_name} {user.last_name}"
        }, room=f"doctor_{appointment.doctor_id}")
        
        return jsonify({
            'message': 'Checked in successfully',
            'queue_entry': queue_entry.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@queue_bp.route('/next/<int:doctor_id>', methods=['POST'])
@jwt_required()
def call_next_patient(doctor_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role not in ['doctor', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get next patient in queue
        next_entry = QueueEntry.query.join(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            QueueEntry.status == 'waiting'
        ).order_by(QueueEntry.queue_position).first()
        
        if not next_entry:
            return jsonify({'error': 'No patients in queue'}), 404
        
        # Update status
        next_entry.status = 'called'
        db.session.commit()
        
        # Emit notification to patient
        socketio.emit('patient_called', {
            'appointment_id': next_entry.appointment_id,
            'message': 'Please proceed to the consultation room'
        }, room=f"patient_{next_entry.appointment.patient_id}")
        
        return jsonify({
            'message': 'Next patient called',
            'appointment': next_entry.appointment.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500