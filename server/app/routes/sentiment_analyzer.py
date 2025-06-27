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
