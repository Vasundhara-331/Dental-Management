from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, socketio
from app.models.user import User, Patient, Doctor
from app.models.appointment import Appointment, QueueEntry
from app.utils.ai_scheduler import SmartScheduler
from app.utils.ai_diagnosis import get_ai_diagnosis
from datetime import datetime, date, time
import json

appointments_bp = Blueprint('appointments', __name__)
scheduler = SmartScheduler()

@appointments_bp.route('', methods=['POST'])
@jwt_required()
def book_appointment():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'patient':
            return jsonify({'error': 'Only patients can book appointments'}), 403
        
        data = request.get_json()
        patient = user.patient_profile
        
        # Get AI diagnosis if symptoms provided
        ai_diagnosis = ""
        urgency_score = 5.0
        
        if data.get('symptoms'):
            diagnosis_result = get_ai_diagnosis(
                symptoms=data['symptoms'],
                tooth_id=data.get('tooth_id'),
                patient_history=patient.medical_history
            )
            ai_diagnosis = diagnosis_result.get('diagnosis', '')
            urgency_score = diagnosis_result.get('urgency_score', 5.0)
        
        # Smart scheduling recommendation
        recommended_slots = scheduler.get_optimal_slots(
            doctor_id=data['doctor_id'],
            urgency_score=urgency_score,
            preferred_date=data.get('preferred_date'),
            duration_minutes=data.get('duration', 30)
        )
        
        # Create appointment
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=data['doctor_id'],
            appointment_date=datetime.strptime(data['appointment_date'], '%Y-%m-%d').date(),
            appointment_time=datetime.strptime(data['appointment_time'], '%H:%M').time(),
            tooth_id=data.get('tooth_id'),
            symptoms=json.dumps(data.get('symptoms', [])) if isinstance(data.get('symptoms'), list) else data.get('symptoms'),
            notes=data.get('notes'),
            ai_diagnosis=ai_diagnosis,
            urgency_score=urgency_score
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        # Emit real-time notification
        socketio.emit('new_appointment', {
            'appointment_id': appointment.id,
            'patient_name': f"{user.first_name} {user.last_name}",
            'doctor_id': data['doctor_id'],
            'urgency_score': urgency_score
        }, room=f"doctor_{data['doctor_id']}")
        
        return jsonify({
            'message': 'Appointment booked successfully',
            'appointment': appointment.to_dict(),
            'recommended_slots': recommended_slots,
            'ai_diagnosis': ai_diagnosis
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('', methods=['GET'])
@jwt_required()
def get_appointments():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role == 'patient':
            appointments = Appointment.query.join(Patient).filter(
                Patient.user_id == user_id
            ).order_by(Appointment.appointment_date.desc()).all()
        
        elif user.role == 'doctor':
            appointments = Appointment.query.join(Doctor).filter(
                Doctor.user_id == user_id
            ).order_by(Appointment.appointment_date.asc()).all()
        
        elif user.role == 'admin':
            appointments = Appointment.query.order_by(
                Appointment.appointment_date.desc()
            ).all()
        
        else:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({
            'appointments': [apt.to_dict() for apt in appointments]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/<int:appointment_id>', methods=['PUT'])
@jwt_required()
def update_appointment(appointment_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        appointment = Appointment.query.get(appointment_id)
        
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404
        
        data = request.get_json()
        
        # Authorization check
        if user.role == 'patient':
            if appointment.patient.user_id != user_id:
                return jsonify({'error': 'Unauthorized'}), 403
            # Patients can only update certain fields
            allowed_fields = ['notes', 'symptoms']
        elif user.role == 'doctor':
            if appointment.doctor.user_id != user_id:
                return jsonify({'error': 'Unauthorized'}), 403
            # Doctors can update treatment-related fields
            allowed_fields = ['status', 'treatment_notes', 'prescription', 'follow_up_date']
        elif user.role == 'admin':
            allowed_fields = list(data.keys())
        else:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Update appointment
        for field in allowed_fields:
            if field in data:
                if field == 'appointment_date':
                    appointment.appointment_date = datetime.strptime(data[field], '%Y-%m-%d').date()
                elif field == 'appointment_time':
                    appointment.appointment_time = datetime.strptime(data[field], '%H:%M').time()
                elif field == 'follow_up_date' and data[field]:
                    appointment.follow_up_date = datetime.strptime(data[field], '%Y-%m-%d').date()
                else:
                    setattr(appointment, field, data[field])
        
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Emit update notification
        socketio.emit('appointment_updated', {
            'appointment_id': appointment.id,
            'status': appointment.status,
            'updated_by': user.role
        })
        
        return jsonify({
            'message': 'Appointment updated successfully',
            'appointment': appointment.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/available-slots', methods=['GET'])
def get_available_slots():
    try:
        doctor_id = request.args.get('doctor_id')
        date_str = request.args.get('date')
        
        if not doctor_id or not date_str:
            return jsonify({'error': 'doctor_id and date are required'}), 400
        
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        doctor = Doctor.query.get(doctor_id)
        
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404
        
        # Get available slots using smart scheduler
        available_slots = scheduler.get_available_slots(doctor_id, target_date)
        
        return jsonify({
            'available_slots': available_slots,
            'doctor': doctor.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500