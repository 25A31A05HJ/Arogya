"""
weekly_report.py
Aggregates a user's last 7 daily_logs rows into the "Weekly AI Health
Report" shown in Section 16 of the project file.
"""


def _avg(values):
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values), 1) if values else 0


def _trend(values):
    """Very simple trend: compare first half average vs second half average."""
    values = [v for v in values if v is not None]
    if len(values) < 2:
        return "steady"
    mid = len(values) // 2
    first_half = _avg(values[:mid]) if mid else values[0]
    second_half = _avg(values[mid:])
    if second_half > first_half * 1.05:
        return "improving"
    if second_half < first_half * 0.95:
        return "declining"
    return "steady"


def build_weekly_report(logs):
    """
    logs: list of daily_log dicts for the last 7 days, oldest first.
          Each dict has sleep_hours, exercise_minutes, water_ml,
          stress_level, wellness_score.
    """
    if not logs:
        return {
            "days_logged": 0,
            "summary": "No activity logged yet this week — start by logging today's sleep, water, and exercise.",
        }

    sleep_values = [l.get("sleep_hours") for l in logs]
    exercise_values = [l.get("exercise_minutes") for l in logs]
    water_values = [l.get("water_ml") for l in logs]
    score_values = [l.get("wellness_score") for l in logs]

    avg_sleep = _avg(sleep_values)
    total_exercise = sum(v for v in exercise_values if v is not None)
    avg_water_l = round(_avg(water_values) / 1000, 2) if water_values else 0
    avg_score = _avg(score_values)

    sleep_trend = _trend(sleep_values)
    exercise_trend = _trend(exercise_values)

    stress_levels = [l.get("stress_level") for l in logs if l.get("stress_level")]
    most_common_stress = max(set(stress_levels), key=stress_levels.count) if stress_levels else "Not logged"

    summary_bits = []
    if exercise_trend == "improving":
        summary_bits.append("Your physical activity improved this week.")
    elif exercise_trend == "declining":
        summary_bits.append("Your physical activity dropped off a bit this week.")
    else:
        summary_bits.append("Your physical activity stayed fairly steady this week.")

    if sleep_trend == "declining" or (sleep_values and max(sleep_values) - min([v for v in sleep_values if v is not None], default=0) > 2):
        summary_bits.append("Your sleep schedule looks somewhat inconsistent — try a fixed bedtime.")
    elif sleep_trend == "improving":
        summary_bits.append("Your sleep consistency is improving — keep it up.")

    return {
        "days_logged": len(logs),
        "avg_sleep_hours": avg_sleep,
        "sleep_trend": sleep_trend,
        "total_exercise_minutes": total_exercise,
        "exercise_trend": exercise_trend,
        "avg_water_liters": avg_water_l,
        "most_common_stress": most_common_stress,
        "avg_wellness_score": avg_score,
        "summary": " ".join(summary_bits),
    }
