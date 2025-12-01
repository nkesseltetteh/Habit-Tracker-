import sqlite3
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd

from database import HabitDatabase
from burnout_predictor import BurnoutPredictor
from sentiment_analyzer import SentimentAnalyzer

# Initialize
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
app.config.suppress_callback_exceptions = True  
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True

# ADD THIS SECTION ↓↓↓
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Habit & Productivity Tracker</title>
        {%favicon%}
        {%css%}
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html> 
'''
db = HabitDatabase()
predictor = BurnoutPredictor(db)

# App layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("🎯 Habit & Productivity Tracker", 
                       className="text-center mb-4 mt-4"), width=12)
    ]),
    
    # Navigation tabs
    dbc.Tabs([
        dbc.Tab(label="Dashboard", tab_id="dashboard"),
        dbc.Tab(label="Add Habit", tab_id="add-habit"),
        dbc.Tab(label="Log Activity", tab_id="log-activity"),
        dbc.Tab(label="Journal", tab_id="journal"),
    ], id="tabs", active_tab="dashboard"),
    
    html.Div(id="tab-content", className="mt-4"),
    
    # Store for data refresh
    dcc.Interval(id='interval-component', interval=60000, n_intervals=0)
], fluid=True)

def render_achievements():
    from gamification import Gamification
    game = Gamification(db)
    
    points = game.calculate_points()
    level, icon, threshold = game.get_level(points)
    achievements = game.check_achievements()
    quote = game.get_motivational_quote()
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3(f"{icon} Level: {level}", className="text-center"),
                        html.H4(f"Points: {points}", className="text-center"),
                        html.Progress(value=str(points % 500), max="500", className="mb-3"),
                        html.P(quote, className="text-center text-muted")
                    ])
                ])
            ], width=12, className="mb-4")
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H4("🏆 Achievements Unlocked"),
                html.Div([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5(f"{icon} {title}"),
                            html.P(description)
                        ])
                    ], className="mb-2")
                    for icon, title, description in achievements
                ])
            ])
        ])
    ])


# Callback to render different tab content
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab")
)
def render_tab_content(active_tab):
    if active_tab == "dashboard":
        return render_dashboard()
    elif active_tab == "add-habit":
        return render_add_habit()
    elif active_tab == "log-activity":
        return render_log_activity()
    elif active_tab == "journal":
        return render_journal()
    elif active_tab == "achievements":  # ← ADD THIS
        return render_achievements()
    return html.Div("Select a tab")

# Dashboard layout
def render_dashboard():
    logs = db.get_habit_logs(days=30)
    burnout_score, recommendation = predictor.calculate_burnout_score(days=14)
    
    if logs.empty:
        return dbc.Container([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-info-circle", style={'fontSize': '48px', 'color': '#667eea'}),
                        html.H4("Welcome to Your Habit Tracker!", className="mt-3"),
                        html.P("Start by adding your first habit, then log your activities to see insights here!"),
                        dbc.Button("Add Your First Habit", color="primary", href="#", id="start-button")
                    ], className="text-center", style={'padding': '40px'})
                ])
            ], className="shadow-lg")
        ])
    
    # Stats cards at top
    total_completions = len(logs)
    avg_mood = round(logs['mood_score'].mean(), 1) if not logs.empty else 0
    unique_habits = logs['name'].nunique()
    
    return dbc.Container([
        # Summary Stats Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.H2("📊", className="mb-0"),
                            html.H3(total_completions, className="mb-0"),
                            html.P("Total Activities", className="text-muted mb-0")
                        ], className="text-center")
                    ])
                ], className="shadow", style={
                    'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    'color': 'white'
                })
            ], width=12, md=4, className="mb-3"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.H2("😊", className="mb-0"),
                            html.H3(f"{avg_mood}/5", className="mb-0"),
                            html.P("Average Mood", className="text-muted mb-0")
                        ], className="text-center")
                    ])
                ], className="shadow", style={
                    'background': 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
                    'color': 'white'
                })
            ], width=12, md=4, className="mb-3"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.H2("🎯", className="mb-0"),
                            html.H3(unique_habits, className="mb-0"),
                            html.P("Active Habits", className="text-muted mb-0")
                        ], className="text-center")
                    ])
                ], className="shadow", style={
                    'background': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                    'color': 'white'
                })
            ], width=12, md=4, className="mb-3"),
        ], className="mb-4"),
        
        # Charts Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4([
                            html.Span("📊 ", className="emoji-icon"),
                            "Habit Completions"
                        ], className="card-title"),
                        dcc.Graph(
                            figure=create_completion_chart(logs),
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="shadow")
            ], width=12, lg=6, className="mb-4"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4([
                            html.Span("📈 ", className="emoji-icon"),
                            "Mood & Energy Trends"
                        ], className="card-title"),
                        dcc.Graph(
                            figure=create_trend_chart(logs),
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="shadow")
            ], width=12, lg=6, className="mb-4"),
        ]),
        
        # Burnout Card
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4([
                            html.Span("🔥 ", className="emoji-icon"),
                            "Burnout Risk Assessment"
                        ], className="card-title"),
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(
                                    figure=create_burnout_gauge(burnout_score),
                                    config={'displayModeBar': False}
                                )
                            ], width=12, md=6),
                            dbc.Col([
                                html.Div([
                                    html.H5("💡 Recommendation", className="mt-3"),
                                    dbc.Alert(
                                        recommendation,
                                        color="success" if burnout_score < 40 else "warning" if burnout_score < 70 else "danger",
                                        className="mt-3"
                                    )
                                ])
                            ], width=12, md=6)
                        ])
                    ])
                ], className="shadow")
            ], width=12)
        ])
    ])

# Helper functions for better charts
def create_completion_chart(logs):
    habit_counts = logs.groupby('name').size().reset_index(name='count')
    fig = px.bar(
        habit_counts,
        x='name',
        y='count',
        labels={'name': 'Habit', 'count': 'Completions'},
        color='count',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        xaxis_title='',
        yaxis_title='Times Completed'
    )
    return fig

def create_trend_chart(logs):
    logs['completed_date'] = pd.to_datetime(logs['completed_date'])
    daily_avg = logs.groupby('completed_date')[['mood_score', 'energy_level']].mean().reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_avg['completed_date'],
        y=daily_avg['mood_score'],
        name='Mood',
        line=dict(color='#667eea', width=3),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.2)'
    ))
    fig.add_trace(go.Scatter(
        x=daily_avg['completed_date'],
        y=daily_avg['energy_level'],
        name='Energy',
        line=dict(color='#38ef7d', width=3),
        fill='tozeroy',
        fillcolor='rgba(56, 239, 125, 0.2)'
    ))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title='',
        yaxis_title='Score (1-5)',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    return fig

def create_burnout_gauge(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': "Risk Level", 'font': {'size': 20}},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkred" if score > 70 else "orange" if score > 40 else "green"},
            'steps': [
                {'range': [0, 40], 'color': "rgba(56, 239, 125, 0.3)"},
                {'range': [40, 70], 'color': "rgba(255, 193, 7, 0.3)"},
                {'range': [70, 100], 'color': "rgba(220, 53, 69, 0.3)"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig
    # Create completion chart
    habit_counts = logs.groupby('name').size().reset_index(name='count')
    completion_fig = px.bar(
        habit_counts,
        x='name',
        y='count',
        title='Habit Completions (Last 30 Days)',
        labels={'name': 'Habit', 'count': 'Times Completed'}
    )
    
    # Create mood/energy trend
    logs['completed_date'] = pd.to_datetime(logs['completed_date'])
    daily_avg = logs.groupby('completed_date')[['mood_score', 'energy_level']].mean().reset_index()
    
    trend_fig = go.Figure()
    trend_fig.add_trace(go.Scatter(
        x=daily_avg['completed_date'],
        y=daily_avg['mood_score'],
        name='Mood',
        line=dict(color='#2ecc71', width=3)
    ))
    trend_fig.add_trace(go.Scatter(
        x=daily_avg['completed_date'],
        y=daily_avg['energy_level'],
        name='Energy',
        line=dict(color='#3498db', width=3)
    ))
    trend_fig.update_layout(
        title='Mood & Energy Trends',
        xaxis_title='Date',
        yaxis_title='Score (1-5)',
        hovermode='x unified'
    )
    
    # Burnout gauge
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=burnout_score,
        title={'text': "Burnout Risk Score"},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkred" if burnout_score > 70 else "orange" if burnout_score > 40 else "green"},
            'steps': [
                {'range': [0, 40], 'color': "lightgreen"},
                {'range': [40, 70], 'color': "lightyellow"},
                {'range': [70, 100], 'color': "lightcoral"}
            ]
        }
    ))
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("📊 Habit Completions", className="card-title"),
                        dcc.Graph(figure=completion_fig)
                    ])
                ])
            ], width=12, className="mb-4")
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("📈 Mood & Energy Trends", className="card-title"),
                        dcc.Graph(figure=trend_fig)
                    ])
                ])
            ], width=12, className="mb-4")
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("🔥 Burnout Risk Assessment", className="card-title"),
                        dcc.Graph(figure=gauge_fig),
                        html.Hr(),
                        html.H5("Recommendation:", className="mt-3"),
                        html.P(recommendation, className="lead")
                    ])
                ])
            ], width=12, className="mb-4")
        ])
    ])

# Add Habit layout
def render_add_habit():
    return dbc.Container([
        dbc.Card([
            dbc.CardBody([
                html.H3([
                    html.Span("➕ ", className="emoji-icon"),
                    "Add New Habit"
                ], className="card-title mb-4"),
                
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Habit Name", html_for="habit-name", className="fw-bold"),
                            dbc.Input(
                                id="habit-name",
                                placeholder="e.g., Morning Jog, Read 30 minutes",
                                type="text",
                                className="mb-3"
                            )
                        ], width=12, md=6)
                    ]),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Category", html_for="habit-category", className="fw-bold"),
                            dbc.Select(
                                id="habit-category",
                                options=[
                                    {"label": "💪 Health", "value": "Health"},
                                    {"label": "💼 Work", "value": "Work"},
                                    {"label": "🏠 Personal", "value": "Personal"},
                                    {"label": "📚 Learning", "value": "Learning"},
                                    {"label": "👥 Social", "value": "Social"}
                                ],
                                className="mb-3"
                            )
                        ], width=12, md=6)
                    ]),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Target Frequency (times per week)", className="fw-bold"),
                            dbc.Input(
                                id="habit-frequency",
                                type="number",
                                min=1,
                                max=7,
                                value=7,
                                className="mb-3"
                            )
                        ], width=12, md=6)
                    ]),
                    
                    dbc.Button(
                        [html.I(className="fas fa-plus me-2"), "Add Habit"],
                        id="add-habit-btn",
                        color="primary",
                        size="lg",
                        className="mt-3"
                    ),
                    
                    html.Div(id="add-habit-output", className="mt-3")
                ])
            ])
        ], className="shadow-lg")
    ])

# Log Activity layout
def render_log_activity():
    habits = db.get_habits()
    
    if habits.empty:
        return dbc.Alert("No habits yet! Add a habit first.", color="warning")
    
    habit_options = [{"label": row['name'], "value": row['id']} for _, row in habits.iterrows()]
    
    return dbc.Container([
        dbc.Card([
            dbc.CardBody([
                html.H3("✅ Log Activity", className="card-title mb-4"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Select Habit"),
                        dbc.Select(id="log-habit-select", options=habit_options)
                    ], width=6)
                ]),
                
                dbc.Row([
    dbc.Col([
        dbc.Label("Date", className="mt-3"),
        dcc.DatePickerSingle(
            id="log-date",
            date=datetime.now().strftime('%Y-%m-%d'),
            display_format='YYYY-MM-DD'
        )
    ], width=6)
]),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Mood Score (1-5)", className="mt-3"),
                        dcc.Slider(id="mood-slider", min=1, max=5, step=1, value=3, marks={i: str(i) for i in range(1, 6)})
                    ], width=6)
                ]),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Energy Level (1-5)", className="mt-3"),
                        dcc.Slider(id="energy-slider", min=1, max=5, step=1, value=3, marks={i: str(i) for i in range(1, 6)})
                    ], width=6)
                ]),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Notes (optional)", className="mt-3"),
                        dbc.Textarea(id="log-notes", placeholder="How did it go?")
                    ], width=12)
                ]),
                
                dbc.Button("Log Activity", id="log-activity-btn", color="success", className="mt-4"),
                html.Div(id="log-activity-output", className="mt-3")
            ])
        ])
    ])

# Journal layout
def render_journal():
    return dbc.Container([
        dbc.Card([
            dbc.CardBody([
                html.H3("📝 Journal Entry", className="card-title mb-4"),
                
                dbc.Row([
    dbc.Col([
        dbc.Label("Date"),
        dcc.DatePickerSingle(
            id="journal-date",
            date=datetime.now().strftime('%Y-%m-%d'),
            display_format='YYYY-MM-DD'
        )
    ], width=6)
]),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Journal Entry", className="mt-3"),
                        dbc.Textarea(id="journal-content", placeholder="How was your day?", style={"height": "200px"})
                    ], width=12)
                ]),
                
                dbc.Button("Save Entry", id="save-journal-btn", color="primary", className="mt-4"),
                html.Div(id="journal-output", className="mt-3")
            ])
        ])
    ])

@app.callback(
    Output("log-activity-output", "children"),
    Input("log-activity-btn", "n_clicks"),
    State("log-habit-select", "value"),
    State("log-date", "date"),
    State("mood-slider", "value"),
    State("energy-slider", "value"),
    State("log-notes", "value"),
    prevent_initial_call=True
)
def log_activity(n_clicks, habit_id, date, mood, energy, notes):
    if not habit_id:
        return dbc.Alert("Please select a habit!", color="danger")
    
    if date:
        date = datetime.fromisoformat(date).strftime('%Y-%m-%d')
    else:
        date = datetime.now().strftime('%Y-%m-%d')
    
    db.log_habit(habit_id, date, notes or "", mood, energy)
    return dbc.Alert("✅ Activity logged successfully!", color="success")

# Duplicate log_activity callback removed (the callback that handles date conversion above is used)

# Callback to save journal
@app.callback(
    Output("journal-output", "children"),
    Input("save-journal-btn", "n_clicks"),
    State("journal-date", "value"),
    State("journal-content", "value"),
    prevent_initial_call=True
)
def save_journal(n_clicks, date, content):
    if not content:
        return dbc.Alert("Please write something in your journal!", color="danger")
    
    # Analyze sentiment
    sentiment = SentimentAnalyzer.analyze_text(content)
    
    # Save to database
    conn = sqlite3.connect(db.db_name)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO journal_entries (entry_date, content, sentiment_score) VALUES (?, ?, ?)',
        (date, content, sentiment)
    )
    conn.commit()
    conn.close()
    
    sentiment_text = SentimentAnalyzer.get_sentiment_category(sentiment)
    return dbc.Alert(f"✅ Journal saved! Sentiment: {sentiment_text}", color="success")

# Run the app
@app.callback(
    Output("streaks-display", "children"),
    Input("interval-component", "n_intervals")
)
def update_streaks(n):
    habits = db.get_habits()
    
    if habits.empty:
        return html.P("No habits yet!")
    
    streak_items = []
    for _, habit in habits.iterrows():
        streak = db.get_current_streak(habit['id'])
        
        if streak > 0:
            streak_items.append(
                html.Div([
                    html.Strong(f"{habit['name']}: "),
                    html.Span(f"🔥 {streak} days", 
                             style={'color': 'orange' if streak >= 7 else 'gray'})
                ], className="mb-2")
            )
    
    return streak_items if streak_items else html.P("Start building streaks!")
if __name__ == '__main__':
    print("=" * 60)
    print("🎯 Habit & Productivity Tracker Starting...")
    print("=" * 60)
    print("📍 Open your browser and go to: http://127.0.0.1:8050")
    print("=" * 60)
    app.run(debug=True, port=8050)