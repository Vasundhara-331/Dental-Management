from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User, Patient, Doctor
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create user
        user = User(
            email=data['email'],
            role=data['role'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Create role-specific profile
        if data['role'] == 'patient':
            patient = Patient(
                user_id=user.id,
                date_of_birth=data.get('date_of_birth'),
                gender=data.get('gender'),
                address=data.get('address'),
                emergency_contact=data.get('emergency_contact'),
                medical_history=data.get('medical_history'),
                allergies=data.get('allergies')
            )
            db.session.add(patient)
        
        elif data['role'] == 'doctor':
            doctor = Doctor(
                user_id=user.id,
                license_number=data['license_number'],
                specialization=data.get('specialization'),
                experience_years=data.get('experience_years'),
                consultation_fee=data.get('consultation_fee'),
                available_days=data.get('available_days', '["Monday","Tuesday","Wednesday","Thursday","Friday"]'),
                available_hours=data.get('available_hours', '09:00-17:00')
            )
            db.session.add(doctor)
        
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        
        if user and user.check_password(data['password']) and user.is_active:
            access_token = create_access_token(
                identity=user.id,
                expires_delta=timedelta(hours=24)
            )
            
            user_data = user.to_dict()
            
            # Add role-specific data
            if user.role == 'patient' and user.patient_profile:
                user_data['profile'] = user.patient_profile.to_dict()
            elif user.role == 'doctor' and user.doctor_profile:
                user_data['profile'] = user.doctor_profile.to_dict()
            
            return jsonify({
                'access_token': access_token,
                'user': user_data
            }), 200
        
        return jsonify({'error': 'Invalid credentials'}), 401
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user_data = user.to_dict()
        
        if user.role == 'patient' and user.patient_profile:
            user_data['profile'] = user.patient_profile.to_dict()
        elif user.role == 'doctor' and user.doctor_profile:
            user_data['profile'] = user.doctor_profile.to_dict()
        
        return jsonify({'user': user_data}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
