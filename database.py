import sqlite3
from datetime import datetime, timedelta
import pandas as pd

class HabitDatabase:
    def __init__(self, db_name='habit_tracker.db'):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize database with tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Create tables (use schema from Step 2)
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                target_frequency INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS habit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER,
                completed_date DATE,
                notes TEXT,
                mood_score INTEGER,
                energy_level INTEGER,
                FOREIGN KEY (habit_id) REFERENCES habits(id)
            );
            
            CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_date DATE,
                content TEXT,
                sentiment_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        conn.commit()
        conn.close()
    
    def add_habit(self, name, category, target_frequency):
        """Add a new habit"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO habits (name, category, target_frequency) VALUES (?, ?, ?)',
            (name, category, target_frequency)
        )
        conn.commit()
        conn.close()
    
    def log_habit(self, habit_id, date, notes, mood_score, energy_level):
        """Log habit completion"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO habit_logs 
               (habit_id, completed_date, notes, mood_score, energy_level) 
               VALUES (?, ?, ?, ?, ?)''',
            (habit_id, date, notes, mood_score, energy_level)
        )
        conn.commit()
        conn.close()
    
    def get_habits(self):
        """Get all habits"""
        conn = sqlite3.connect(self.db_name)
        df = pd.read_sql_query('SELECT * FROM habits', conn)
        conn.close()
        return df
    
    def get_habit_logs(self, days=30):
        """Get habit logs for the last N days"""
        conn = sqlite3.connect(self.db_name)
        query = '''
            SELECT hl.*, h.name, h.category 
            FROM habit_logs hl
            JOIN habits h ON hl.habit_id = h.id
            WHERE hl.completed_date >= date('now', '-{} days')
        '''.format(days)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_current_streak(self, habit_id):
        """Calculate current streak for a habit"""
        conn = sqlite3.connect(self.db_name)
        logs = pd.read_sql_query(
            f'''SELECT completed_date 
                FROM habit_logs 
                WHERE habit_id = {habit_id} 
                ORDER BY completed_date DESC''',
            conn
        )
        conn.close()
        
        if logs.empty:
            return 0
        
        streak = 0
        current_date = datetime.now().date()
        
        for _, row in logs.iterrows():
            log_date = datetime.strptime(row['completed_date'], '%Y-%m-%d').date()
            if (current_date - log_date).days == streak:
                streak += 1
            else:
                break
        
        return streak
    
    def calculate_completion_rate(self, habit_id, days=7):
        """Calculate what % of target was achieved"""
        habits = self.get_habits()
        habit = habits[habits['id'] == habit_id]
        
        if habit.empty:
            return 0
        
        target = habit.iloc[0]['target_frequency']
        
        logs = self.get_habit_logs(days=days)
        actual = len(logs[logs['habit_id'] == habit_id])
        
        return (actual / target * 100) if target > 0 else 0
    
    def generate_weekly_report(self):
        """Generate summary of the past week"""
        logs = self.get_habit_logs(days=7)
        
        if logs.empty:
            return None
        
        report = {
            'total_completions': len(logs),
            'avg_mood': round(logs['mood_score'].mean(), 1),
            'avg_energy': round(logs['energy_level'].mean(), 1),
            'most_completed': logs['name'].mode()[0] if len(logs) > 0 else 'None',
            'unique_habits': logs['name'].nunique()
        }
        
        return report
    
    def export_to_csv(self, filename='habit_data_export.csv'):
        """Export all data to CSV"""
        logs = self.get_habit_logs(days=365)
        logs.to_csv(filename, index=False)
        return filename