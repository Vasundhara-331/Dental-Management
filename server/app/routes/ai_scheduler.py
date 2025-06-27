from datetime import datetime, date, time, timedelta
from app.models.appointment import Appointment
from app.models.user import Doctor
from app import db
import json

class SmartScheduler:
    def __init__(self):
        self.slot_duration = 30  # minutes
        self.break_duration = 15  # minutes between slots
    
    def get_available_slots(self, doctor_id, target_date):
        """Get available time slots for a doctor on a specific date"""
        try:
            doctor = Doctor.query.get(doctor_id)
            if not doctor:
                return []
            
            # Parse available hours
            available_hours = doctor.available_hours.split('-')
            start_hour = int(available_hours[0].split(':')[0])
            end_hour = int(available_hours[1].split(':')[0])
            
            # Generate time slots
            slots = []
            current_time = time(start_hour, 0)
            end_time = time(end_hour, 0)
            
            while current_time < end_time:
                # Check if slot is available
                existing_appointment = Appointment.query.filter(
                    Appointment.doctor_id == doctor_id,
                    Appointment.appointment_date == target_date,
                    Appointment.appointment_time == current_time,
                    Appointment.status.in_(['scheduled', 'confirmed'])
                ).first()
                
                if not existing_appointment:
                    slots.append(current_time.strftime('%H:%M'))
                
                # Move to next slot
                current_datetime = datetime.combine(date.today(), current_time)
                next_datetime = current_datetime + timedelta(minutes=self.slot_duration)
                current_time = next_datetime.time()
            
            return slots
        
        except Exception as e:
            print(f"Error getting available slots: {e}")
            return []
    
    def get_optimal_slots(self, doctor_id, urgency_score, preferred_date=None, duration_minutes=30):
        """Get optimal appointment slots based on urgency and preferences"""
        try:
            if preferred_date:
                target_date = datetime.strptime(preferred_date, '%Y-%m-%d').date()
            else:
                target_date = date.today() + timedelta(days=1)
            
            recommendations = []
            
            # Check multiple days
            for i in range(7):  # Check next 7 days
                check_date = target_date + timedelta(days=i)
                available_slots = self.get_available_slots(doctor_id, check_date)
                
                for slot in available_slots:
                    priority_score = self._calculate_priority_score(
                        urgency_score, check_date, slot, i
                    )
                    
                    recommendations.append({
                        'date': check_date.isoformat(),
                        'time': slot,
                        'priority_score': priority_score,
                        'urgency_match': urgency_score > 7.0 and i == 0,
                        'recommended': priority_score > 8.0
                    })
            
            # Sort by priority score
            recommendations.sort(key=lambda x: x['priority_score'], reverse=True)
            
            return recommendations[:10]  # Return top 10 recommendations
        
        except Exception as e:
            print(f"Error getting optimal slots: {e}")
            return []
    
    def _calculate_priority_score(self, urgency_score, slot_date, slot_time, days_ahead):
        """Calculate priority score for a time slot"""
        base_score = 5.0
        
        # Urgency factor
        if urgency_score > 8.0:
            base_score += 3.0
        elif urgency_score > 6.0:
            base_score += 1.0
        
        # Date factor (sooner is better for urgent cases)
        if urgency_score > 7.0:
            base_score += max(0, 3.0 - days_ahead * 0.5)
        
        # Time factor (morning slots generally preferred)
        hour = int(slot_time.split(':')[0])
        if 9 <= hour <= 11:
            base_score += 1.0
        elif 14 <= hour <= 16:
            base_score += 0.5
        
        # Weekend penalty
        if slot_date.weekday() >= 5:
            base_score -= 0.5
        
        return min(base_score, 10.0)