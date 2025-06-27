from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User, Doctor

doctors_bp = Blueprint('doctors', __name__)

@doctors_bp.route('', methods=['GET'])
def get_doctors():
    try:
        doctors = db.session.query(Doctor, User).join(
            User, Doctor.user_id == User.id
        ).filter(User.is_active == True).all()
        
        doctor_list = []
        for doctor, user in doctors:
            doctor_data = doctor.to_dict()
            doctor_data.update({
                'name': f"{user.first_name} {user.last_name}",
                'email': user.email,
                'phone': user.phone
            })
            doctor_list.append(doctor_data)
        
        return jsonify({'doctors': doctor_list}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@doctors_bp.route('/<int:doctor_id>', methods=['GET'])
def get_doctor(doctor_id):
    try:
        doctor, user = db.session.query(Doctor, User).join(
            User, Doctor.user_id == User.id
        ).filter(Doctor.id == doctor_id).first()
        
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404
        
        doctor_data = doctor.to_dict()
        doctor_data.update({
            'name': f"{user.first_name} {user.last_name}",
            'email': user.email,
            'phone': user.phone
        })
        
        return jsonify({'doctor': doctor_data}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@doctors_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_doctor_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'doctor':
            return jsonify({'error': 'Only doctors can update doctor profile'}), 403
        
        doctor = user.doctor_profile
        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404
        
        data = request.get_json()
        
        # Update doctor fields
        allowed_fields = ['specialization', 'experience_years', 'consultation_fee', 
                         'available_days', 'available_hours']
        
        for field in allowed_fields:
            if field in data:
                setattr(doctor, field, data[field])
        
        # Update user fields
        user_fields = ['first_name', 'last_name', 'phone']
        for field in user_fields:
            if field in data:
                setattr(user, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'doctor': doctor.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
