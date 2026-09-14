"""
seed_demo_data.py

Creates a demo user with a week of sample daily_logs so the dashboard,
trend chart, and weekly report have something to show immediately —
useful for a hackathon demo.

Run from the backend/ directory:
    python seed_demo_data.py
"""
import json
from datetime import date, timedelta

from werkzeug.security import generate_password_hash

import db
from ai_engine.wellness_score import compute_wellness_score

DEMO_EMAIL = "demo@aarogyaai.app"
DEMO_PASSWORD = "demo1234"

# (days_ago, sleep_hours, water_ml, exercise_minutes, stress_level, nutrition_rating)
SAMPLE_WEEK = [
    (6, 5.0, 1200, 15, "Stressed", "Fair"),
    (5, 5.5, 1400, 20, "Stressed", "Fair"),
    (4, 6.0, 1600, 25, "Okay", "Good"),
    (3, 6.5, 1700, 30, "Okay", "Good"),
    (2, 6.0, 1800, 35, "Good", "Good"),
    (1, 7.0, 2000, 40, "Good", "Excellent"),
    (0, 6.5, 1800, 40, "Medium".replace("Medium", "Okay"), "Good"),
]


def seed():
    db.init_db()

    existing = db.query_one("SELECT user_id FROM users WHERE email = ?", (DEMO_EMAIL,))
    if existing:
        user_id = existing["user_id"]
        print(f"Demo user already exists (user_id={user_id}) — refreshing logs.")
        db.execute("DELETE FROM daily_logs WHERE user_id = ?", (user_id,))
        db.execute("DELETE FROM exercise_entries WHERE user_id = ?", (user_id,))
        db.execute("DELETE FROM meal_entries WHERE user_id = ?", (user_id,))
    else:
        user_id, _ = db.execute(
            """INSERT INTO users
               (name, email, password_hash, age, height_cm, weight_kg,
                activity_level, wellness_goal, diet_preference,
                water_goal_ml, sleep_goal_hrs)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "Demo User", DEMO_EMAIL, generate_password_hash(DEMO_PASSWORD),
                20, 170, 65, "Moderate", "Improve fitness", "Vegetarian", 2000, 8,
            ),
        )
        print(f"Created demo user (user_id={user_id}).")

    for days_ago, sleep_hours, water_ml, exercise_minutes, stress_level, nutrition_rating in SAMPLE_WEEK:
        log_date = (date.today() - timedelta(days=days_ago)).isoformat()
        db.execute(
            """INSERT INTO daily_logs
               (user_id, log_date, sleep_hours, water_ml, exercise_minutes,
                stress_level, nutrition_rating)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, log_date, sleep_hours, water_ml, exercise_minutes, stress_level, nutrition_rating),
        )
        score = compute_wellness_score(
            {
                "sleep_hours": sleep_hours, "water_ml": water_ml,
                "exercise_minutes": exercise_minutes, "stress_level": stress_level,
                "nutrition_rating": nutrition_rating,
            }
        )
        db.execute(
            "UPDATE daily_logs SET wellness_score = ?, score_breakdown = ? WHERE user_id = ? AND log_date = ?",
            (score["overall"], json.dumps(score["breakdown"]), user_id, log_date),
        )

    print(f"Seeded {len(SAMPLE_WEEK)} days of demo data.")
    print(f"Log in with: {DEMO_EMAIL} / {DEMO_PASSWORD}")


if __name__ == "__main__":
    seed()
