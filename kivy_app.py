from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider
from kivy.uix.scrollview import ScrollView
from datetime import datetime
import traceback

# Try to import database modules
try:
    from database import HabitDatabase
    from burnout_predictor import BurnoutPredictor
    from sentiment_analyzer import SentimentAnalyzer
    
    db = HabitDatabase()
    predictor = BurnoutPredictor(db)
    IMPORTS_OK = True
    IMPORT_ERROR = None
except Exception as e:
    IMPORTS_OK = False
    IMPORT_ERROR = str(e)
    print("ERROR importing:", e)


class DashboardTab(BoxLayout):
    """Dashboard showing stats"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10
        
        if not IMPORTS_OK:
            self.add_widget(Label(text=f'Error: {IMPORT_ERROR}', color=(1, 0, 0, 1)))
            return
        
        try:
            # Title
            self.add_widget(Label(text='📊 Dashboard', font_size='24sp', size_hint_y=0.1))
            
            # Get data
            logs = db.get_habit_logs(days=30)
            
            if logs.empty:
                self.add_widget(Label(text='No data yet!\nAdd habits and log activities.'))
            else:
                # Stats scroll view
                scroll = ScrollView(size_hint=(1, 0.7))
                stats_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
                # Call bind via getattr to avoid static type-checker errors that don't recognize BoxLayout.bind
                getattr(stats_box, 'bind')(minimum_height=lambda x, y: setattr(stats_box, 'height', y))
                
                # Show habit counts
                habit_counts = logs.groupby('name').size()
                for habit, count in habit_counts.items():
                    stats_box.add_widget(Label(
                        text=f'{habit}: {count} times',
                        size_hint_y=None,
                        height=40,
                        color=(0, 0.5, 1, 1)
                    ))
                
                scroll.add_widget(stats_box)
                self.add_widget(scroll)
                self.add_widget(Label(text='🔥 Current Streaks:', font_size='20sp'))
            
                habits = db.get_habits()
                for _, habit in habits.iterrows():
                    streak = db.get_current_streak(habit['id'])
                    if streak > 0:
                        self.add_widget(Label(
                            text=f"{habit['name']}: {streak} days",
                            color=(1, 0.5, 0, 1) if streak >= 7 else (0.7, 0.7, 0.7, 1)
                        ))
                        
                        # Burnout score
                        burnout_score, recommendation = predictor.calculate_burnout_score()
                        self.add_widget(Label(
                            text=f'🔥 Burnout Risk: {burnout_score}%\n{recommendation}',
                            size_hint_y=0.2
                        ))
        except Exception as e:
            self.add_widget(Label(text=f'Error: {str(e)}', color=(1, 0, 0, 1)))
            print("Dashboard error:", e)
            traceback.print_exc()


class AddHabitTab(BoxLayout):
    """Add new habits"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        
        # Title
        self.add_widget(Label(text='➕ Add New Habit', font_size='24sp', size_hint_y=0.1))
        
        # Habit name
        self.add_widget(Label(text='Habit Name:', size_hint_y=0.08))
        self.habit_name = TextInput(hint_text='e.g., Morning Jog', size_hint_y=0.1, multiline=False)
        self.add_widget(self.habit_name)
        
        # Category
        self.add_widget(Label(text='Category:', size_hint_y=0.08))
        self.category = Spinner(
            text='Health',
            values=['Health', 'Work', 'Personal', 'Learning', 'Social'],
            size_hint_y=0.1
        )
        self.add_widget(self.category)
        
        # Frequency
        self.add_widget(Label(text='Target Frequency (times/week):', size_hint_y=0.08))
        self.frequency = Slider(min=1, max=7, value=7, size_hint_y=0.1)
        self.freq_label = Label(text='7 times/week', size_hint_y=0.08)
        getattr(self.frequency, 'bind')(value=self.update_freq)
        self.add_widget(self.frequency)
        self.add_widget(self.freq_label)
        
        # Add button
        add_btn = Button(text='Add Habit', size_hint_y=0.12, background_color=(0, 0.7, 0, 1))
        getattr(add_btn, 'bind')(on_press=self.add_habit)
        self.add_widget(add_btn)
        
        # Status
        self.status = Label(text='', size_hint_y=0.15, color=(0, 1, 0, 1))
        self.add_widget(self.status)
    
    def update_freq(self, instance, value):
        self.freq_label.text = f'{int(value)} times/week'
    
    def add_habit(self, instance):
        try:
            name = self.habit_name.text
            category = self.category.text
            frequency = int(self.frequency.value)
            
            if not name:
                self.status.text = '❌ Please enter a habit name!'
                self.status.color = (1, 0, 0, 1)
                return
            
            db.add_habit(name, category, frequency)
            self.status.text = f'✅ Habit "{name}" added!'
            self.status.color = (0, 1, 0, 1)
            self.habit_name.text = ''
        except Exception as e:
            self.status.text = f'Error: {str(e)}'
            self.status.color = (1, 0, 0, 1)
            print("Add habit error:", e)


class LogActivityTab(BoxLayout):
    """Log habit completion"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        
        # Title
        self.add_widget(Label(text='✅ Log Activity', font_size='24sp', size_hint_y=0.1))
        
        try:
            habits = db.get_habits()
            
            if habits.empty:
                self.add_widget(Label(text='No habits yet!\nAdd a habit first.'))
                return
            
            # Habit selector
            habit_names = habits['name'].tolist()
            self.habit_ids = dict(zip(habit_names, habits['id'].tolist()))
            
            self.add_widget(Label(text='Select Habit:', size_hint_y=0.08))
            self.habit_spinner = Spinner(
                text=habit_names[0],
                values=habit_names,
                size_hint_y=0.1
            )
            self.add_widget(self.habit_spinner)
            
            # Mood
            self.add_widget(Label(text='Mood Score (1-5):', size_hint_y=0.08))
            self.mood = Slider(min=1, max=5, value=3, size_hint_y=0.1)
            self.mood_label = Label(text='3', size_hint_y=0.08)
            getattr(self.mood, 'bind')(value=lambda i, v: setattr(self.mood_label, 'text', str(int(v))))
            self.add_widget(self.mood)
            self.add_widget(self.mood_label)
            
            # Energy
            self.add_widget(Label(text='Energy Level (1-5):', size_hint_y=0.08))
            self.energy = Slider(min=1, max=5, value=3, size_hint_y=0.1)
            self.energy_label = Label(text='3', size_hint_y=0.08)
            getattr(self.energy, 'bind')(value=lambda i, v: setattr(self.energy_label, 'text', str(int(v))))
            self.add_widget(self.energy)
            self.add_widget(self.energy_label)
            
            # Notes
            self.add_widget(Label(text='Notes:', size_hint_y=0.08))
            self.notes = TextInput(hint_text='How did it go?', size_hint_y=0.15)
            self.add_widget(self.notes)
            
            # Log button
            log_btn = Button(text='Log Activity', size_hint_y=0.12, background_color=(0, 0.7, 0, 1))
            getattr(log_btn, 'bind')(on_press=self.log_activity)
            self.add_widget(log_btn)
            
            # Status
            self.status = Label(text='', size_hint_y=0.1, color=(0, 1, 0, 1))
            self.add_widget(self.status)
            
        except Exception as e:
            self.add_widget(Label(text=f'Error: {str(e)}', color=(1, 0, 0, 1)))
            print("Log activity tab error:", e)
    
    def log_activity(self, instance):
        try:
            habit_name = self.habit_spinner.text
            habit_id = self.habit_ids[habit_name]
            date = datetime.now().strftime('%Y-%m-%d')
            mood = int(self.mood.value)
            energy = int(self.energy.value)
            notes = self.notes.text
            
            db.log_habit(habit_id, date, notes, mood, energy)
            self.status.text = '✅ Activity logged successfully!'
            self.status.color = (0, 1, 0, 1)
            self.notes.text = ''
        except Exception as e:
            self.status.text = f'Error: {str(e)}'
            self.status.color = (1, 0, 0, 1)
            print("Log activity error:", e)


class JournalTab(BoxLayout):
    """Journal entries"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        
        # Title
        self.add_widget(Label(text='📝 Journal Entry', font_size='24sp', size_hint_y=0.1))
        
        # Journal text
        self.add_widget(Label(text='How was your day?', size_hint_y=0.08))
        self.journal_text = TextInput(size_hint_y=0.5)
        self.add_widget(self.journal_text)
        
        # Save button
        save_btn = Button(text='Save Entry', size_hint_y=0.12, background_color=(0, 0.7, 0, 1))
        getattr(save_btn, 'bind')(on_press=self.save_journal)
        self.add_widget(save_btn)
        
        # Status
        self.status = Label(text='', size_hint_y=0.2, color=(0, 1, 0, 1))
        self.add_widget(self.status)
    
    def save_journal(self, instance):
        try:
            content = self.journal_text.text
            
            if not content:
                self.status.text = '❌ Please write something!'
                self.status.color = (1, 0, 0, 1)
                return
            
            sentiment = SentimentAnalyzer.analyze_text(content)
            sentiment_category = SentimentAnalyzer.get_sentiment_category(sentiment)
            
            import sqlite3
            conn = sqlite3.connect(db.db_name)
            cursor = conn.cursor()
            date = datetime.now().strftime('%Y-%m-%d')
            cursor.execute(
                'INSERT INTO journal_entries (entry_date, content, sentiment_score) VALUES (?, ?, ?)',
                (date, content, sentiment)
            )
            conn.commit()
            conn.close()
            
            self.status.text = f'✅ Saved! Sentiment: {sentiment_category}'
            self.status.color = (0, 1, 0, 1)
            self.journal_text.text = ''
        except Exception as e:
            self.status.text = f'Error: {str(e)}'
            self.status.color = (1, 0, 0, 1)
            print("Journal error:", e)


class HabitTrackerApp(App):
    """Main app"""
    
    def build(self):
        try:
            # Create tabbed panel
            panel = TabbedPanel(do_default_tab=False)
            
            # Add tabs
            tab1 = TabbedPanelItem(text='Dashboard')
            tab1.add_widget(DashboardTab())
            panel.add_widget(tab1)
            
            tab2 = TabbedPanelItem(text='Add Habit')
            tab2.add_widget(AddHabitTab())
            panel.add_widget(tab2)
            
            tab3 = TabbedPanelItem(text='Log Activity')
            tab3.add_widget(LogActivityTab())
            panel.add_widget(tab3)
            
            tab4 = TabbedPanelItem(text='Journal')
            tab4.add_widget(JournalTab())
            panel.add_widget(tab4)
            
            return panel
        except Exception as e:
            print("BUILD ERROR:", e)
            traceback.print_exc()
            return Label(text=f'Error building app:\n{str(e)}')


if __name__ == '__main__':
    print("=" * 50)
    print("Starting Habit Tracker...")
    print("=" * 50)
    HabitTrackerApp().run()