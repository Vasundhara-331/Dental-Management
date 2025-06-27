from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User, Patient
from app.models.patient_history import PatientHistory
from app.models.appointment import Appointment

patients_bp = Blueprint('patients', __name__)

@patients_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_patient_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'patient':
            return jsonify({'error': 'Only patients can access patient profile'}), 403
        
        patient = user.patient_profile
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        return jsonify({
            'patient': patient.to_dict(),
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patients_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_patient_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'patient':
            return jsonify({'error': 'Only patients can update patient profile'}), 403
        
        patient = user.patient_profile
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404
        
        data = request.get_json()
        
        # Update patient fields
        patient_fields = ['date_of_birth', 'gender', 'address', 'emergency_contact', 
                         'medical_history', 'allergies']
        
        for field in patient_fields:
            if field in data:
                setattr(patient, field, data[field])
        
        # Update user fields
        user_fields = ['first_name', 'last_name', 'phone']
        for field in user_fields:
            if field in data:
                setattr(user, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'patient': patient.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@patients_bp.route('/history', methods=['GET'])
@jwt_required()
def get_patient_history():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'patient':
            return jsonify({'error': 'Only patients can access patient history'}), 403
        
        patient = user.patient_profile
        history = PatientHistory.query.filter_by(patient_id=patient.id).order_by(
            PatientHistory.visit_date.desc()
        ).all()
        
        return jsonify({
            'history': [h.to_dict() for h in history]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patients_bp.route('/health-score', methods=['GET'])
@jwt_required()
def get_health_score():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'patient':
            return jsonify({'error': 'Only patients can access health score'}), 403
        
        patient = user.patient_profile
        
        # Calculate health score based on various factors
        score = patient.dental_health_score
        
        # Get recent appointments for score calculation
        recent_appointments = Appointment.query.filter_by(
            patient_id=patient.id
        ).order_by(Appointment.appointment_date.desc()).limit(5).all()
        
        score_factors = {
            'regular_checkups': 0,
            'treatment_compliance': 0,
            'oral_hygiene': 0,
            'follow_up_adherence': 0
        }
        
        return jsonify({
            'dental_health_score': score,
            'score_factors': score_factors,
            'recent_visits': len(recent_appointments),
            'next_recommended_visit': patient.last_visit
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
