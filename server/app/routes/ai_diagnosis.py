import openai
import os
from datetime import datetime
import json

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_ai_diagnosis(symptoms, tooth_id=None, patient_history=None):
    """Get AI-powered preliminary diagnosis"""
    try:
        # Prepare context
        context = f"Patient symptoms: {symptoms}"
        if tooth_id:
            context += f"\nAffected tooth: {tooth_id}"
        if patient_history:
            context += f"\nPatient history: {patient_history}"
        
        # Simple rule-based diagnosis (replace with OpenAI API call)
        diagnosis_result = _rule_based_diagnosis(symptoms, tooth_id)
        
        return diagnosis_result
    
    except Exception as e:
        print(f"Error in AI diagnosis: {e}")
        return {
            'diagnosis': 'Unable to analyze symptoms at this time',
            'urgency_score': 5.0,
            'recommendations': ['Please consult with a dentist']
        }

def analyze_symptoms(symptoms, tooth_id=None, additional_info=''):
    """Analyze symptoms and provide recommendations"""
    try:
        symptoms_text = ' '.join(symptoms) if isinstance(symptoms, list) else symptoms
        
        analysis = {
            'primary_concern': _identify_primary_concern(symptoms_text),
            'urgency_level': _determine_urgency(symptoms_text),
            'possible_conditions': _identify_conditions(symptoms_text),
            'recommendations': _generate_recommendations(symptoms_text),
            'suggested_treatments': _suggest_treatments(symptoms_text)
        }
        
        return analysis
    
    except Exception as e:
        print(f"Error analyzing symptoms: {e}")
        return {
            'primary_concern': 'General dental consultation needed',
            'urgency_level': 'medium',
            'possible_conditions': ['Requires professional examination'],
            'recommendations': ['Schedule dental appointment'],
            'suggested_treatments': ['Professional consultation']
        }

def _rule_based_diagnosis(symptoms, tooth_id):
    """Simple rule-based diagnosis system"""
    symptoms_text = ' '.join(symptoms) if isinstance(symptoms, list) else symptoms
    symptoms_lower = symptoms_text.lower()
    
    diagnosis = "General dental consultation recommended"
    urgency_score = 5.0
    recommendations = []
    
    # Pain-related symptoms
    if any(word in symptoms_lower for word in ['severe pain', 'excruciating', 'unbearable']):
        diagnosis = "Severe dental pain - possible acute pulpitis or abscess"
        urgency_score = 9.0
        recommendations = ['Immediate dental attention required', 'Pain management needed']
    
    elif any(word in symptoms_lower for word in ['sharp pain', 'shooting pain']):
        diagnosis = "Sharp dental pain - possible nerve involvement"
        urgency_score = 7.5
        recommendations = ['Urgent dental appointment', 'Avoid hot/cold foods']
    
    elif 'toothache' in symptoms_lower or 'tooth pain' in symptoms_lower:
        diagnosis = "Dental pain - possible caries or sensitivity"
        urgency_score = 6.0
        recommendations = ['Schedule dental appointment', 'Use pain relief if needed']
    
    # Sensitivity symptoms
    elif any(word in symptoms_lower for word in ['sensitivity', 'sensitive']):
        diagnosis = "Tooth sensitivity - possible enamel erosion or exposed dentin"
        urgency_score = 4.0
        recommendations = ['Use desensitizing toothpaste', 'Avoid acidic foods']
    
    # Bleeding symptoms
    elif 'bleeding' in symptoms_lower:
        diagnosis = "Gum bleeding - possible gingivitis or periodontitis"
        urgency_score = 5.5
        recommendations = ['Improve oral hygiene', 'Professional cleaning needed']
    
    # Swelling symptoms
    elif 'swelling' in symptoms_lower or 'swollen' in symptoms_lower:
        diagnosis = "Dental swelling - possible infection or abscess"
        urgency_score = 8.0
        recommendations = ['Urgent dental attention', 'Possible antibiotic treatment needed']
    
    return {
        'diagnosis': diagnosis,
        'urgency_score': urgency_score,
        'recommendations': recommendations
    }

def _identify_primary_concern(symptoms_text):
    """Identify the primary dental concern"""
    symptoms_lower = symptoms_text.lower()
    
    if 'pain' in symptoms_lower:
        return 'Dental pain'
    elif 'bleeding' in symptoms_lower:
        return 'Gum bleeding'
    elif 'sensitivity' in symptoms_lower:
        return 'Tooth sensitivity'
    elif 'swelling' in symptoms_lower:
        return 'Dental swelling'
    else:
        return 'General dental concern'

def _determine_urgency(symptoms_text):
    """Determine urgency level"""
    symptoms_lower = symptoms_text.lower()
    
    if any(word in symptoms_lower for word in ['severe', 'excruciating', 'unbearable', 'emergency']):
        return 'high'
    elif any(word in symptoms_lower for word in ['moderate', 'sharp', 'throbbing']):
        return 'medium'
    else:
        return 'low'

def _identify_conditions(symptoms_text):
    """Identify possible dental conditions"""
    symptoms_lower = symptoms_text.lower()
    conditions = []
    
    if 'pain' in symptoms_lower:
        conditions.extend(['Dental caries', 'Pulpitis', 'Abscess'])
    if 'bleeding' in symptoms_lower:
        conditions.extend(['Gingivitis', 'Periodontitis'])
    if 'sensitivity' in symptoms_lower:
        conditions.extend(['Enamel erosion', 'Exposed dentin'])
    if 'swelling' in symptoms_lower:
        conditions.extend(['Dental abscess', 'Cellulitis'])
    
    return conditions if conditions else ['Requires professional examination']

def _generate_recommendations(symptoms_text):
    """Generate recommendations based on symptoms"""
    symptoms_lower = symptoms_text.lower()
    recommendations = []
    
    if 'pain' in symptoms_lower:
        recommendations.extend(['Take over-the-counter pain relief', 'Avoid hot/cold foods'])
    if 'bleeding' in symptoms_lower:
        recommendations.extend(['Gentle brushing', 'Use antibacterial mouthwash'])
    if 'sensitivity' in symptoms_lower:
        recommendations.extend(['Use desensitizing toothpaste', 'Avoid acidic foods'])
    if 'swelling' in symptoms_lower:
        recommendations.extend(['Apply cold compress', 'Seek immediate dental care'])
    
    recommendations.append('Schedule dental appointment')
    return recommendations

def _suggest_treatments(symptoms_text):
    """Suggest possible treatments"""
    symptoms_lower = symptoms_text.lower()
    treatments = []
    
    if 'pain' in symptoms_lower:
        treatments.extend(['Dental filling', 'Root canal therapy', 'Pain management'])
    if 'bleeding' in symptoms_lower:
        treatments.extend(['Professional cleaning', 'Periodontal therapy'])
    if 'sensitivity' in symptoms_lower:
        treatments.extend(['Fluoride treatment', 'Desensitizing agents'])
    if 'swelling' in symptoms_lower:
        treatments.extend(['Antibiotic therapy', 'Drainage procedure'])
    
    treatments.append('Professional consultation')
    return treatments

# server/app/utils/sentiment_analyzer.py
from textblob import TextBlob

def analyze_patient_sentiment(text):
    """Analyze patient sentiment from text input"""
    try:
        blob = TextBlob(text)
        sentiment = blob.sentiment
        
        # Determine emotional state
        if sentiment.polarity > 0.3:
            emotion = 'positive'
        elif sentiment.polarity < -0.3:
            emotion = 'negative'
        else:
            emotion = 'neutral'
        
        # Determine anxiety level based on subjectivity and negative sentiment
        anxiety_indicators = ['worried', 'scared', 'anxious', 'nervous', 'afraid']
        anxiety_level = 'low'
        
        if any(indicator in text.lower() for indicator in anxiety_indicators):
            anxiety_level = 'high'
        elif sentiment.subjectivity > 0.7 and sentiment.polarity < 0:
            anxiety_level = 'medium'
        
        return {
            'polarity': sentiment.polarity,
            'subjectivity': sentiment.subjectivity,
            'emotion': emotion,
            'anxiety_level': anxiety_level,
            'requires_reassurance': anxiety_level in ['medium', 'high']
        }
    
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return {
            'polarity': 0.0,
            'subjectivity': 0.0,
            'emotion': 'neutral',
            'anxiety_level': 'low',
            'requires_reassurance': False
        }