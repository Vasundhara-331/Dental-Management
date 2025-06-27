from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.ai_diagnosis import get_ai_diagnosis, analyze_symptoms
import json

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/symptoms', methods=['POST'])
@jwt_required()
def analyze_patient_symptoms():
    try:
        data = request.get_json()
        symptoms = data.get('symptoms', [])
        tooth_id = data.get('tooth_id')
        additional_info = data.get('additional_info', '')
        message = ''
        if isinstance(symptoms, list):
            message = ' '.join(symptoms)
        elif isinstance(symptoms, str):
            message = symptoms
        else:
            message = str(symptoms)

        if not symptoms:
            return jsonify({'error': 'Symptoms are required'}), 400

        # Keyword-based dummy analysis
        keyword_analysis = {
            'pain': {
                'analysis': 'Pain detected. Possible cavity or infection.',
                'recommendations': ['Visit dentist soon', 'Pain relief medication'],
                'urgency_level': 'high',
                'suggested_treatments': ['X-ray', 'Filling']
            },
            'bleeding': {
                'analysis': 'Bleeding detected. Possible gum disease.',
                'recommendations': ['Gentle brushing', 'Visit dentist'],
                'urgency_level': 'medium',
                'suggested_treatments': ['Scaling', 'Antibiotics']
            },
            'sensitivity': {
                'analysis': 'Sensitivity detected. Possible enamel wear.',
                'recommendations': ['Use sensitive toothpaste'],
                'urgency_level': 'low',
                'suggested_treatments': ['Fluoride treatment']
            },
            'swelling': {
                'analysis': 'Swelling detected. Possible infection.',
                'recommendations': ['Apply cold compress', 'Visit dentist'],
                'urgency_level': 'high',
                'suggested_treatments': ['Antibiotics', 'Drainage']
            },
        }
        found = False
        for keyword, result in keyword_analysis.items():
            if keyword in message.lower():
                found = True
                return jsonify(result), 200
        # Default response
        return jsonify({
            'analysis': 'Symptoms noted. Please provide more details or consult a dentist.',
            'recommendations': ['Book an appointment', 'Describe symptoms in detail'],
            'urgency_level': 'medium',
            'suggested_treatments': []
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chatbot_bp.route('/chat', methods=['POST'])
@jwt_required()
def chat_with_bot():
    try:
        data = request.get_json()
        message = data.get('message', '')
        context = data.get('context', {})
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        # Simple chatbot responses (can be enhanced with OpenAI API)
        responses = {
            'tooth pain': 'I understand you\'re experiencing tooth pain. Can you describe the pain? Is it sharp, throbbing, or constant?',
            'bleeding gums': 'Bleeding gums can indicate gum disease. How long have you noticed the bleeding?',
            'sensitivity': 'Tooth sensitivity can be caused by several factors. When do you notice the sensitivity most?',
            'emergency': 'This sounds like it might need immediate attention. I recommend booking an urgent appointment.',
            'hello': 'Hello! I\'m here to help you with your dental concerns. What symptoms are you experiencing?',
            'appointment': 'I can help you book an appointment. What type of dental issue would you like to address?'
        }
        # Simple keyword matching (enhance with NLP)
        response = "I understand your concern. Can you provide more details about your symptoms?"
        for keyword, reply in responses.items():
            if keyword.lower() in message.lower():
                response = reply
                break
        return jsonify({
            'response': response,
            'suggestions': [
                'Book an appointment',
                'Describe symptoms in detail',
                'Emergency consultation'
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
