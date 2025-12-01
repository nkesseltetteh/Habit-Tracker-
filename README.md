

🎯 Habit & Productivity Tracker

A smart, interactive dashboard for building habits, tracking mood, detecting burnout early, and boosting productivity!

This project is built with a beautiful UI, powerful analytics, and even an **AI-powered sentiment analyzer** to give meaningful insights into your daily journal entries. It brings together data tracking, visualization, wellness monitoring, and gamification — all in one place!

---
🌟 Features

* 📊 **Interactive Productivity Dashboard**
  Visualizes habit completions, mood trends, energy levels, and burnout risk.

* 📝 **AI-Powered Journal Analysis**
  Automatically analyzes the sentiment of your daily journal entries.

* 🔥 **Burnout Prediction Engine**
  Uses historic mood and activity data to estimate burnout risk and provide recommendations.

* 🏆 **Gamification System**
  Earn points, unlock achievements, and level up based on consistent habits.

* ➕ **Add Habits Easily**
  Fully customizable habit creation with categories and weekly targets.

* ✅ **Log Daily Activities**
  Track mood, energy, progress notes, and completion frequency.

---

🧰 Tools, Libraries & Technologies Used

This project is powered by a rich ecosystem of Python tools and frameworks:

 **📦 Core Libraries**

* **Dash** – For building the interactive dashboard and UI components
* **Dash Bootstrap Components (DBC)** – For stylish, responsive layouts
* **Plotly (graph_objects + express)** – For beautiful data visualizations
* **Pandas** – For efficient data manipulation and analysis
* **SQLite3** – Lightweight database storage

 **🤖 AI / Analytics Modules**

* **SentimentAnalyzer** – NLP-powered sentiment scoring for journal entries
* **BurnoutPredictor** – A custom model that detects burnout risk
* **Gamification Engine** – Calculates points, achievements, and motivational messages

 **📁 Project Modules**

* `database.py` – Manages habits, logs, streaks, and journals
* `burnout_predictor.py` – Predicts burnout levels from trends
* `sentiment_analyzer.py` – Analyzes emotional tone of journal content
* `gamification.py` – Handles leveling, points, and badges
* `App.py` – Main Dash application tying everything together

---
 🚀 How to Run Locally

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
2. Start the app:

   ```bash
   python App.py
   ```
3. Open your browser and go to:
   **[http://127.0.0.1:8050](http://127.0.0.1:8050)**

---

## 📌 Future Enhancements

* User authentication
* More advanced burnout models
* Mobile-friendly layout improvements
* Cloud sync and remote database option

---

