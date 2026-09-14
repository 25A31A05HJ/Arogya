import json
from datetime import date, timedelta

from flask import Blueprint, request, jsonify, current_app

import db
from utils.auth_utils import token_required
from ai_engine.safety_rules import check_red_flags
from ai_engine.wellness_score import compute_wellness_score

daily_log_bp = Blueprint("daily_log", __name__, url_prefix="/api/logs")


def _today():
    return date.today().isoformat()


def _get_user(user_id):
    return db.query_one(
        "SELECT sleep_goal_hrs, water_goal_ml FROM users WHERE user_id = ?", (user_id,)
    )


def _get_or_create_today(user_id, log_date):
    row = db.query_one(
        "SELECT * FROM daily_logs WHERE user_id = ? AND log_date = ?",
        (user_id, log_date),
    )
    if row:
        return row
    log_id, _ = db.execute(
        "INSERT INTO daily_logs (user_id, log_date) VALUES (?, ?)",
        (user_id, log_date),
    )
    return db.query_one("SELECT * FROM daily_logs WHERE log_id = ?", (log_id,))


def _recompute_and_save(user_id, log_date):
    """Recalculate the wellness score for a day after any field changes."""
    row = db.query_one(
        "SELECT * FROM daily_logs WHERE user_id = ? AND log_date = ?",
        (user_id, log_date),
    )
    user = _get_user(user_id)
    result = compute_wellness_score(
        row,
        sleep_goal_hrs=user["sleep_goal_hrs"] if user else 8,
        water_goal_ml=user["water_goal_ml"] if user else 2000,
    )
    db.execute(
        """UPDATE daily_logs
           SET wellness_score = ?, score_breakdown = ?, updated_at = CURRENT_TIMESTAMP
           WHERE user_id = ? AND log_date = ?""",
        (result["overall"], json.dumps(result["breakdown"]), user_id, log_date),
    )
    return result


@daily_log_bp.route("/today", methods=["GET"])
@token_required
def get_today():
    row = _get_or_create_today(request.user_id, _today())
    return jsonify(row)


@daily_log_bp.route("/today", methods=["POST"])
@token_required
def update_today():
    """
    Upserts today's sleep / water / stress / symptoms fields.
    Body (all optional, send whatever the user is logging right now):
      { "sleep_hours": 6.5, "water_ml_add": 300, "stress_level": "Stressed",
        "mood_note": "...", "symptoms_text": "..." }
    """
    data = request.get_json(force=True) or {}
    log_date = _today()
    _get_or_create_today(request.user_id, log_date)

    safety_result = None
    if data.get("symptoms_text"):
        safety_result = check_red_flags(data["symptoms_text"])

    fields, params = [], []
    if "sleep_hours" in data:
        fields.append("sleep_hours = ?")
        params.append(data["sleep_hours"])
    if "water_ml_add" in data:
        fields.append("water_ml = COALESCE(water_ml, 0) + ?")
        params.append(data["water_ml_add"])
    if "stress_level" in data:
        fields.append("stress_level = ?")
        params.append(data["stress_level"])
    if "mood_note" in data:
        fields.append("mood_note = ?")
        params.append(data["mood_note"])
    if "symptoms_text" in data:
        fields.append("symptoms_text = ?")
        params.append(data["symptoms_text"])

    if fields:
        params += [request.user_id, log_date]
        db.execute(
            f"UPDATE daily_logs SET {', '.join(fields)} WHERE user_id = ? AND log_date = ?",
            params,
        )

    score = _recompute_and_save(request.user_id, log_date)
    row = db.query_one(
        "SELECT * FROM daily_logs WHERE user_id = ? AND log_date = ?",
        (request.user_id, log_date),
    )

    response = {"log": row, "wellness_score": score}
    if safety_result and safety_result["is_emergency"]:
        response["safety_alert"] = safety_result["message"]
    return jsonify(response)


@daily_log_bp.route("/exercise", methods=["POST"])
@token_required
def add_exercise():
    data = request.get_json(force=True) or {}
    activity = data.get("activity")
    minutes = data.get("minutes")
    if not activity or not minutes:
        return jsonify({"error": "activity and minutes are required"}), 400

    log_date = _today()
    _get_or_create_today(request.user_id, log_date)

    db.execute(
        "INSERT INTO exercise_entries (user_id, log_date, activity, minutes) VALUES (?, ?, ?, ?)",
        (request.user_id, log_date, activity, minutes),
    )
    db.execute(
        """UPDATE daily_logs
           SET exercise_minutes = COALESCE(exercise_minutes, 0) + ?
           WHERE user_id = ? AND log_date = ?""",
        (minutes, request.user_id, log_date),
    )
    score = _recompute_and_save(request.user_id, log_date)

    entries = db.query_all(
        "SELECT activity, minutes FROM exercise_entries WHERE user_id = ? AND log_date = ?",
        (request.user_id, log_date),
    )
    return jsonify({"entries": entries, "wellness_score": score})


@daily_log_bp.route("/meal", methods=["POST"])
@token_required
def add_meal():
    data = request.get_json(force=True) or {}
    meal_type = data.get("meal_type")
    description = data.get("description")
    nutrition_rating = data.get("nutrition_rating")  # optional, self-reported
    if not meal_type or not description:
        return jsonify({"error": "meal_type and description are required"}), 400

    log_date = _today()
    _get_or_create_today(request.user_id, log_date)

    db.execute(
        "INSERT INTO meal_entries (user_id, log_date, meal_type, description) VALUES (?, ?, ?, ?)",
        (request.user_id, log_date, meal_type, description),
    )
    if nutrition_rating:
        db.execute(
            "UPDATE daily_logs SET nutrition_rating = ? WHERE user_id = ? AND log_date = ?",
            (nutrition_rating, request.user_id, log_date),
        )
    score = _recompute_and_save(request.user_id, log_date)

    meals = db.query_all(
        "SELECT meal_type, description FROM meal_entries WHERE user_id = ? AND log_date = ?",
        (request.user_id, log_date),
    )
    return jsonify({"meals": meals, "wellness_score": score})


@daily_log_bp.route("/history", methods=["GET"])
@token_required
def get_history():
    days = int(request.args.get("days", 7))
    start_date = (date.today() - timedelta(days=days - 1)).isoformat()

    rows = db.query_all(
        """SELECT * FROM daily_logs
           WHERE user_id = ? AND log_date >= ?
           ORDER BY log_date ASC""",
        (request.user_id, start_date),
    )
    return jsonify(rows)
