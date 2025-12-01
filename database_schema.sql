-- habits table
CREATE TABLE habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    target_frequency INTEGER,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- habit_logs table
CREATE TABLE habit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER,
    completed_date DATE,
    notes TEXT,
    mood_score INTEGER,
    energy_level INTEGER,
    FOREIGN KEY (habit_id) REFERENCES habits(id)
);

-- journal_entries table
CREATE TABLE journal_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_date DATE,
    content TEXT,
    sentiment_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);