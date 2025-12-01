from datetime import datetime, timedelta

class Gamification:
    def __init__(self, database):
        self.db = database
    
    def calculate_points(self):
        """Calculate total points"""
        logs = self.db.get_habit_logs(days=365)
        
        points = 0
        points += len(logs) * 10  # 10 points per completion
        
        # Bonus for high mood
        high_mood = len(logs[logs['mood_score'] >= 4])
        points += high_mood * 5
        
        # Bonus for streaks
        habits = self.db.get_habits()
        for _, habit in habits.iterrows():
            streak = self.db.get_current_streak(habit['id'])
            points += streak * 2
        
        return points
    
    def get_level(self, points):
        """Calculate user level"""
        levels = [
            (0, "Novice", "🌱"),
            (100, "Beginner", "🌿"),
            (500, "Intermediate", "🌳"),
            (1000, "Advanced", "🏆"),
            (2500, "Expert", "💎"),
            (5000, "Master", "👑")
        ]
        
        for threshold, title, icon in reversed(levels):
            if points >= threshold:
                return title, icon, threshold
        
        return "Novice", "🌱", 0
    
    def check_achievements(self):
        """Check which achievements user has earned"""
        logs = self.db.get_habit_logs(days=365)
        achievements = []
        
        # Total completions
        total = len(logs)
        if total >= 10:
            achievements.append(("🎯", "First Steps", "Logged 10 activities"))
        if total >= 50:
            achievements.append(("⭐", "Committed", "Logged 50 activities"))
        if total >= 100:
            achievements.append(("🏆", "Century Club", "Logged 100 activities"))
        if total >= 365:
            achievements.append(("👑", "Year Warrior", "Logged 365 activities"))
        
        # Streaks
        habits = self.db.get_habits()
        max_streak = 0
        for _, habit in habits.iterrows():
            streak = self.db.get_current_streak(habit['id'])
            max_streak = max(max_streak, streak)
        
        if max_streak >= 3:
            achievements.append(("🔥", "On Fire", "3 day streak"))
        if max_streak >= 7:
            achievements.append(("💪", "Week Warrior", "7 day streak"))
        if max_streak >= 30:
            achievements.append(("💎", "Month Master", "30 day streak"))
        
        # Mood achievements
        if not logs.empty:
            avg_mood = logs['mood_score'].mean()
            if avg_mood >= 4.5:
                achievements.append(("😊", "Happy Soul", "Average mood 4.5+"))
        
        return achievements
    
    def get_motivational_quote(self):
        """Return a random motivational quote"""
        import random
        quotes = [
            "Small steps lead to big changes! 💪",
            "You're building a better you! 🌟",
            "Consistency is key! 🔑",
            "Every day is a fresh start! 🌅",
            "Progress, not perfection! 📈",
            "You're doing amazing! Keep going! 🎯",
            "Your future self will thank you! 🙏"
        ]
        return random.choice(quotes)