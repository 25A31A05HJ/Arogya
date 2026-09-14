import json
from datetime import date

from flask import Blueprint, request, jsonify

import db
from utils.auth_utils import token_required
from ai_engine.wellness_score import compute_wellness_score, strongest_and_weakest
from ai_engine.recommendations import generate_recommendations

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("", methods=["GET"])
@token_required
def dashboard():
    log_date = date.today().isoformat()
    row = db.query_one(
        "SELECT * FROM daily_logs WHERE user_id = ? AND log_date = ?",
        (request.user_id, log_date),
    )
    user = db.query_one(
        "SELECT sleep_goal_hrs, water_goal_ml, wellness_goal FROM users WHERE user_id = ?",
        (request.user_id,),
    )

    if not row:
        # No entry yet today — return a zeroed dashboard rather than an error.
        row = {
            "sleep_hours": 0, "water_ml": 0, "exercise_minutes": 0,
            "stress_level": None, "nutrition_rating": None,
        }

    score = compute_wellness_score(
        row,
        sleep_goal_hrs=user["sleep_goal_hrs"] if user else 8,
        water_goal_ml=user["water_goal_ml"] if user else 2000,
    )
    strongest, weakest = strongest_and_weakest(score["breakdown"])
    recommendations = generate_recommendations(score["breakdown"])

    insight = (
        f"Your strongest area today is {strongest}. "
        f"{weakest.capitalize()} is the main area that could use attention."
    )

    return jsonify({
        "date": log_date,
        "sleep_hours": row.get("sleep_hours") or 0,
        "water_ml": row.get("water_ml") or 0,
        "exercise_minutes": row.get("exercise_minutes") or 0,
        "stress_level": row.get("stress_level"),
        "nutrition_rating": row.get("nutrition_rating"),
        "wellness_score": score["overall"],
        "score_breakdown": score["breakdown"],
        "insight": insight,
        "recommendations": recommendations,
    })
