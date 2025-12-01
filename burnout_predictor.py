import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class BurnoutPredictor:
    def __init__(self, database):
        self.db = database
    
    def calculate_burnout_score(self, days=14):
        """Calculate burnout risk score based on recent data"""
        logs = self.db.get_habit_logs(days=days)
        
        if logs.empty:
            return 0, "Insufficient data"
        
        # Factors that contribute to burnout
        factors = {
            'low_energy': 0,
            'low_mood': 0,
            'declining_completion': 0,
            'negative_sentiment': 0
        }
        
        # Calculate average energy and mood
        avg_energy = logs['energy_level'].mean()
        avg_mood = logs['mood_score'].mean()
        
        # Low energy indicator (scale 1-5, below 2.5 is concerning)
        if avg_energy < 2.5:
            factors['low_energy'] = (2.5 - avg_energy) / 2.5 * 30
        
        # Low mood indicator
        if avg_mood < 2.5:
            factors['low_mood'] = (2.5 - avg_mood) / 2.5 * 30
        
        # Declining completion rate
        first_half = logs[logs['completed_date'] <= 
                         (datetime.now() - timedelta(days=days//2)).strftime('%Y-%m-%d')]
        second_half = logs[logs['completed_date'] > 
                          (datetime.now() - timedelta(days=days//2)).strftime('%Y-%m-%d')]
        
        if not first_half.empty and not second_half.empty:
            completion_decline = (len(first_half) - len(second_half)) / len(first_half)
            if completion_decline > 0:
                factors['declining_completion'] = int(completion_decline * 25)
        
        # Sentiment in notes
        if 'notes' in logs.columns:
            from sentiment_analyzer import SentimentAnalyzer
            sentiments = logs['notes'].apply(SentimentAnalyzer.analyze_text)
            avg_sentiment = sentiments.mean()
            if avg_sentiment < -0.2:
                factors['negative_sentiment'] = abs(avg_sentiment) * 15
        
        # Calculate total burnout score (0-100)
        burnout_score = min(sum(factors.values()), 100)
        
        # Generate recommendation
        if burnout_score > 70:
            recommendation = "High burnout risk! Consider taking a break and reducing commitments."
        elif burnout_score > 40:
            recommendation = "Moderate burnout risk. Focus on self-care and prioritize rest."
        else:
            recommendation = "You're doing well! Keep maintaining balance."
        
        return round(burnout_score, 1), recommendation

    
    def find_correlations(self):
        """Find relationships between habits and mood/energy"""
        logs = self.db.get_habit_logs(days=30)
        
        if logs.empty:
            return "Not enough data yet"
        
        insights = []
        
        # Group by category
        for category in logs['category'].unique():
            cat_logs = logs[logs['category'] == category]
            cat_avg_energy = cat_logs['energy_level'].mean()
            overall_avg = logs['energy_level'].mean()
            
            diff = cat_avg_energy - overall_avg
            
            if diff > 0.5:
                insights.append(f"✨ {category} habits boost your energy by {diff:.1f} points!")
            elif diff < -0.5:
                insights.append(f"⚠️ {category} habits drain your energy by {abs(diff):.1f} points")
        
        return insights if insights else ["Keep logging to discover patterns!"]
    
    def predict_next_week(self):
        """Predict burnout risk for next week"""
        # Get trend from last 2 weeks
        week1 = self.db.get_habit_logs(days=14)
        week2 = self.db.get_habit_logs(days=7)
        
        if week1.empty or week2.empty:
            return "Need more data"
        
        energy_trend = week2['energy_level'].mean() - week1['energy_level'].mean()
        
        if energy_trend < -0.5:
            return "⚠️ Warning: Energy declining. Consider lighter week ahead."
        elif energy_trend > 0.5:
            return "📈 Trending up! You're gaining momentum."
        else:
            return "➡️ Stable. Maintain current routine."
    
    def get_best_performing_habits(self):
        """Find habits that correlate with best mood"""
        logs = self.db.get_habit_logs(days=30)
        
        if logs.empty:
            return []
        
        habit_moods = logs.groupby('name')['mood_score'].mean().sort_values(ascending=False)
        
        return habit_moods.head(3).to_dict()