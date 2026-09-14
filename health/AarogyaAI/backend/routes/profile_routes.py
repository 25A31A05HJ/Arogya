from flask import Blueprint, request, jsonify

import db
from utils.auth_utils import token_required

profile_bp = Blueprint("profile", __name__, url_prefix="/api/profile")

EDITABLE_FIELDS = [
    "name", "age", "height_cm", "weight_kg", "activity_level",
    "wellness_goal", "diet_preference", "water_goal_ml", "sleep_goal_hrs",
]


@profile_bp.route("", methods=["GET"])
@token_required
def get_profile():
    user = db.query_one(
        """SELECT user_id, name, email, age, height_cm, weight_kg,
                  activity_level, wellness_goal, diet_preference,
                  water_goal_ml, sleep_goal_hrs, created_at
           FROM users WHERE user_id = ?""",
        (request.user_id,),
    )
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)


@profile_bp.route("", methods=["PUT"])
@token_required
def update_profile():
    data = request.get_json(force=True) or {}
    updates = {k: v for k, v in data.items() if k in EDITABLE_FIELDS}
    if not updates:
        return jsonify({"error": "No editable fields provided"}), 400

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    params = list(updates.values()) + [request.user_id]
    db.execute(f"UPDATE users SET {set_clause} WHERE user_id = ?", params)

    return jsonify({"message": "Profile updated"})
